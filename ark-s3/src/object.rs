use aws_sdk_s3::{
    error::SdkError,
    operation::get_object_attributes::{GetObjectAttributesError, GetObjectAttributesOutput},
    Client,
};

pub async fn get_object_attributes(
    client: &Client,
    bucket_name: &str,
    key: &str,
) -> Result<GetObjectAttributesOutput, SdkError<GetObjectAttributesError>> {
    client
        .get_object_attributes()
        .bucket(bucket_name)
        .key(key)
        .object_attributes(aws_sdk_s3::types::ObjectAttributes::ObjectSize)
        .send()
        .await
}
