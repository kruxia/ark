use aws_config::meta::region::RegionProviderChain;
use aws_config::BehaviorVersion;
use aws_sdk_s3::{Client, Error};

pub fn client() -> Client {
    let endpoint_url = env!("AWS_S3_ENDPOINT_URL").to_string();
    let region_provider = RegionProviderChain::default_provider().or_else("us-east-1");
    let config = aws_config::from_env()
        .region(region_provider)
        .endpoint_url(endpoint_url)
        .load()
        .await;
    let client = Client::new(&config);
    tracing::debug!("{client:?}");
    client
}

async fn create_bucket(
    client: &Client,
    bucket_name: &str,
    region: &str,
) -> Result<CreateBucketOutput, SdkError<CreateBucketError>> {
    let constraint = BucketLocationConstraint::from(region);
    let cfg = CreateBucketConfiguration::builder()
        .location_constraint(constraint)
        .build();
    client
        .create_bucket()
        .create_bucket_configuration(cfg)
        .bucket(bucket_name)
        .send()
        .await
}

async fn list_buckets(client: &Client) -> Result<(), Error> {
    let resp = client.list_buckets().send().await?;
    let buckets = resp.buckets();
    let num_buckets = buckets.len();

    for bucket in buckets {
        println!("{}", bucket.name().unwrap_or_default());
    }

    println!();
    println!("Found {} buckets.", num_buckets);

    Ok(())
}
