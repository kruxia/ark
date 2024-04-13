use aws_sdk_s3::{
    error::SdkError,
    operation::{
        create_bucket::{CreateBucketError, CreateBucketOutput},
        list_buckets::{ListBucketsError, ListBucketsOutput},
    },
    types::{BucketLocationConstraint, CreateBucketConfiguration},
    Client,
};

pub async fn exists(client: &Client, name: &str) -> bool {
    let result = client.head_bucket().bucket(name).send().await;
    match result {
        Ok(_) => true,
        _ => false,
    }
}

pub async fn create(
    client: &Client,
    name: &str,
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
