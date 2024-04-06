use aws_sdk_s3::{
    config::{Builder, Credentials, Region},
    Client, Config,
};

pub fn new_client() -> Client {
    let endpoint_url = std::env::var("S3_ENDPOINT_URL").unwrap();
    let access_key_id = std::env::var("AWS_ACCESS_KEY_ID").unwrap();
    let secret_access_key = std::env::var("AWS_SECRET_ACCESS_KEY").unwrap();
    let region_name = std::env::var("AWS_REGION").unwrap();

    println!("endpoint_url = {}", endpoint_url);
    println!("access_key_id = {}", access_key_id);
    println!("secret_access_key = {}", secret_access_key);
    println!("region_name = {}", region_name);

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
