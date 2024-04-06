use aws_sdk_s3::{
    error::SdkError,
    operation::{
        create_bucket::{CreateBucketError, CreateBucketOutput},
        list_buckets::{ListBucketsError, ListBucketsOutput},
    },
    types::{BucketLocationConstraint, CreateBucketConfiguration},
    Client,
};

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
