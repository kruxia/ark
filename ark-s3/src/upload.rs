use aws_sdk_s3::{
    error::SdkError,
    operation::put_object::{PutObjectError, PutObjectOutput},
    primitives::ByteStream,
    Client,
};
use std::path::Path;

pub async fn upload_object_filepath(
    client: &Client,
    bucket_name: &str,
    filepath: &Path,
    key: &str,
) -> Result<PutObjectOutput, SdkError<PutObjectError>> {
    let body = ByteStream::from_path(filepath).await.unwrap();
    client
        .put_object()
        .bucket(bucket_name)
        .key(key)
        .body(body)
        .send()
        .await
}

pub async fn upload_object_stream(
    client: &Client,
    bucket_name: &str,
    stream: ByteStream,
    key: &str,
) -> Result<PutObjectOutput, SdkError<PutObjectError>> {
    client
        .put_object()
        .bucket(bucket_name)
        .key(key)
        .body(stream)
        .send()
        .await
}
