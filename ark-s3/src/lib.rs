use aws_sdk_s3::config::{Builder, Credentials, Region};

use aws_sdk_s3::operation::create_bucket::{CreateBucketError, CreateBucketOutput};
use aws_sdk_s3::operation::list_buckets::{ListBucketsError, ListBucketsOutput};
use aws_sdk_s3::types::{BucketLocationConstraint, CreateBucketConfiguration};
use aws_sdk_s3::{error::SdkError, Client, Config};

pub fn new_client() -> Client {
    let endpoint_url = std::env::var("S3_ENDPOINT_URL").unwrap();
    let access_key_id = std::env::var("AWS_ACCESS_KEY_ID").unwrap();
    let secret_access_key = std::env::var("AWS_SECRET_ACCESS_KEY").unwrap();
    let region_name = std::env::var("AWS_REGION").unwrap();

    let config: Config = Builder::new()
        .behavior_version_latest()
        .region(Region::new(region_name))
        .credentials_provider(Credentials::new(
            access_key_id,
            secret_access_key,
            None,
            None,
            "",
        ))
        .endpoint_url(endpoint_url)
        .force_path_style(true)
        .build();

    aws_sdk_s3::Client::from_conf(config)
}

pub async fn create_bucket(
    client: &Client,
    name: String,
) -> Result<CreateBucketOutput, SdkError<CreateBucketError>> {
    let constraint = BucketLocationConstraint::from("");
    let cfg = CreateBucketConfiguration::builder()
        .location_constraint(constraint)
        .build();

    client
        .create_bucket()
        .create_bucket_configuration(cfg)
        .bucket(format!("{name}"))
        .send()
        .await
}

pub async fn list_buckets(
    client: &Client,
) -> Result<ListBucketsOutput, SdkError<ListBucketsError>> {
    client.list_buckets().send().await
}
