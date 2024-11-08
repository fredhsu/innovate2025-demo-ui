// Cargo.toml
[package]
name = "tenant-network-api"
version = "0.1.0"
edition = "2021"

[dependencies]
axum = "0.7"
tokio = { version = "1.0", features = ["full"] }
sqlx = { version = "0.7", features = ["runtime-tokio-native-tls", "postgres", "json", "ipnetwork"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tower = "0.4"
tower-http = { version = "0.5", features = ["trace"] }
dotenv = "0.15"
thiserror = "1.0"
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
validator = { version = "0.16", features = ["derive"] }
ipnetwork = "0.20"

// src/main.rs
mod handlers;
mod models;
mod errors;
mod state;

use axum::{
    routing::{get, post, put, delete},
    Router,
};
use dotenv::dotenv;
use sqlx::postgres::PgPoolOptions;
use std::net::SocketAddr;
use tower_http::trace::TraceLayer;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

use state::AppState;

#[tokio::main]
async fn main() {
    dotenv().ok();

    // Initialize tracing
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::new(
            std::env::var("RUST_LOG").unwrap_or_else(|_| "info".into()),
        ))
        .with(tracing_subscriber::fmt::layer())
        .init();

    // Create database connection pool
    let database_url = std::env::var("DATABASE_URL")
        .expect("DATABASE_URL must be set");

    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&database_url)
        .await
        .expect("Failed to create pool");

    let state = AppState { pool };

    // Build our application router
    let app = Router::new()
        // Tenant routes
        .route("/tenants", post(handlers::create_tenant))
        .route("/tenants", get(handlers::list_tenants))
        .route("/tenants/:id", get(handlers::get_tenant))
        .route("/tenants/:id", put(handlers::update_tenant))
        .route("/tenants/:id", delete(handlers::delete_tenant))
        // VRF routes
        .route("/vrfs", post(handlers::create_vrf))
        .route("/vrfs/:id", get(handlers::get_vrf))
        .route("/vrfs/:id", put(handlers::update_vrf))
        .route("/vrfs/:id", delete(handlers::delete_vrf))
        // SVI routes
        .route("/svis", post(handlers::create_svi))
        .route("/svis/:id", get(handlers::get_svi))
        .route("/svis/:id", put(handlers::update_svi))
        .route("/svis/:id", delete(handlers::delete_svi))
        .layer(TraceLayer::new_for_http())
        .with_state(state);

    let addr = SocketAddr::from(([127, 0, 0, 1], 3000));
    tracing::info!("listening on {}", addr);
    
    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await
        .unwrap();
}

// src/state.rs
use sqlx::PgPool;

#[derive(Clone)]
pub struct AppState {
    pub pool: PgPool,
}

// src/models.rs
use ipnetwork::IpNetwork;
use serde::{Deserialize, Serialize};
use validator::Validate;

#[derive(Debug, Serialize, Deserialize, Validate)]
pub struct Tenant {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tenant_id: Option<i32>,
    #[validate(length(min = 1, max = 255))]
    pub name: String,
    pub mac_vrf_vni_base: i32,
}

#[derive(Debug, Serialize, Deserialize, Validate)]
pub struct Vrf {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub vrf_id: Option<i32>,
    pub tenant_id: i32,
    #[validate(length(min = 1, max = 255))]
    pub name: String,
    pub vrf_vni: i32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VtepDiagnostic {
    pub vtep_id: Option<i32>,
    pub vrf_id: i32,
    pub loopback: i32,
    pub loopback_ip_range: IpNetwork,
}

#[derive(Debug, Serialize, Deserialize, Validate)]
pub struct Svi {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub svi_id: Option<i32>,
    pub vrf_id: i32,
    pub vlan_id: i32,
    #[validate(length(min = 1, max = 255))]
    pub name: String,
    pub enabled: bool,
    pub ip_address_virtual: Option<IpNetwork>,
    pub tags: Vec<String>,
}

// src/errors.rs
use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde_json::json;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ApiError {
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),
    #[error("Validation error: {0}")]
    Validation(String),
    #[error("Not found")]
    NotFound,
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        let (status, error_message) = match self {
            ApiError::Database(err) => {
                tracing::error!("Database error: {:?}", err);
                (StatusCode::INTERNAL_SERVER_ERROR, "Internal server error")
            }
            ApiError::Validation(err) => (StatusCode::BAD_REQUEST, err.as_str()),
            ApiError::NotFound => (StatusCode::NOT_FOUND, "Resource not found"),
        };

        let body = Json(json!({
            "error": error_message,
        }));

        (status, body).into_response()
    }
}

// src/handlers.rs
use axum::{
    extract::{Path, State},
    Json,
};
use validator::Validate;

use crate::{models::*, errors::ApiError, state::AppState};

pub async fn create_tenant(
    State(state): State<AppState>,
    Json(tenant): Json<Tenant>,
) -> Result<(StatusCode, Json<Tenant>), ApiError> {
    tenant.validate()
        .map_err(|e| ApiError::Validation(e.to_string()))?;

    let tenant = sqlx::query_as!(
        Tenant,
        r#"
        INSERT INTO tenants (name, mac_vrf_vni_base)
        VALUES ($1, $2)
        RETURNING tenant_id, name, mac_vrf_vni_base
        "#,
        tenant.name,
        tenant.mac_vrf_vni_base
    )
    .fetch_one(&state.pool)
    .await?;

    Ok((StatusCode::CREATED, Json(tenant)))
}

pub async fn get_tenant(
    State(state): State<AppState>,
    Path(id): Path<i32>,
) -> Result<Json<Tenant>, ApiError> {
    let tenant = sqlx::query_as!(
        Tenant,
        "SELECT * FROM tenants WHERE tenant_id = $1",
        id
    )
    .fetch_optional(&state.pool)
    .await?
    .ok_or(ApiError::NotFound)?;

    Ok(Json(tenant))
}

pub async fn update_tenant(
    State(state): State<AppState>,
    Path(id): Path<i32>,
    Json(tenant): Json<Tenant>,
) -> Result<Json<Tenant>, ApiError> {
    tenant.validate()
        .map_err(|e| ApiError::Validation(e.to_string()))?;

    let tenant = sqlx::query_as!(
        Tenant,
        r#"
        UPDATE tenants
        SET name = $1, mac_vrf_vni_base = $2
        WHERE tenant_id = $3
        RETURNING tenant_id, name, mac_vrf_vni_base
        "#,
        tenant.name,
        tenant.mac_vrf_vni_base,
        id
    )
    .fetch_optional(&state.pool)
    .await?
    .ok_or(ApiError::NotFound)?;

    Ok(Json(tenant))
}

pub async fn delete_tenant(
    State(state): State<AppState>,
    Path(id): Path<i32>,
) -> Result<StatusCode, ApiError> {
    let result = sqlx::query!(
        "DELETE FROM tenants WHERE tenant_id = $1",
        id
    )
    .execute(&state.pool)
    .await?;

    if result.rows_affected() == 0 {
        return Err(ApiError::NotFound);
    }

    Ok(StatusCode::NO_CONTENT)
}

pub async fn list_tenants(
    State(state): State<AppState>,
) -> Result<Json<Vec<Tenant>>, ApiError> {
    let tenants = sqlx::query_as!(
        Tenant,
        "SELECT * FROM tenants ORDER BY tenant_id"
    )
    .fetch_all(&state.pool)
    .await?;

    Ok(Json(tenants))
}

pub async fn create_svi(
    State(state): State<AppState>,
    Json(svi): Json<Svi>,
) -> Result<(StatusCode, Json<Svi>), ApiError> {
    svi.validate()
        .map_err(|e| ApiError::Validation(e.to_string()))?;

    let mut tx = state.pool.begin().await?;

    let svi_result = sqlx::query_as!(
        Svi,
        r#"
        INSERT INTO svis (vrf_id, vlan_id, name, enabled, ip_address_virtual)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING svi_id, vrf_id, vlan_id, name, enabled, ip_address_virtual
        "#,
        svi.vrf_id,
        svi.vlan_id,
        svi.name,
        svi.enabled,
        svi.ip_address_virtual as Option<IpNetwork>
    )
    .fetch_one(&mut *tx)
    .await?;

    for tag in &svi.tags {
        sqlx::query!(
            r#"
            INSERT INTO svi_tags (svi_id, tag)
            VALUES ($1, $2)
            "#,
            svi_result.svi_id,
            tag
        )
        .execute(&mut *tx)
        .await?;
    }

    tx.commit().await?;

    Ok((StatusCode::CREATED, Json(svi_result)))
}

// Implement remaining VRF and SVI handlers similarly...
