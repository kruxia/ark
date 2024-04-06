use ark_s3::{bucket, client, object, upload};
use aws_sdk_s3::primitives::ByteStream;
use std::env;
use std::path::Path;

#[tokio::main]
async fn main() {
    let client = client::new_client();
    let bucket_name = String::from("test-bucket");
    let create_bucket_result = bucket::create_bucket(&client, bucket_name).await;
    println!("{:?}", create_bucket_result);
    let list_buckets_result = bucket::list_buckets(&client).await;
    match list_buckets_result {
        Ok(result) => {
            let buckets = result.buckets();
            let n = buckets.len();

            println!("{} bucket{}:", n, if n != 1 { "s" } else { "" });
            for bucket in buckets {
                println!("- {}", bucket.name().unwrap());
            }
        }
        Err(err) => println!("{:?}", err),
    };
    // upload listed files (from the commandline args)
    println!("Args:");
    for (index, filepath) in env::args().enumerate() {
        print!("  {index} {filepath} ... ");
        let path = Path::new(&filepath);
        if path.is_file() {
            let stream = ByteStream::from_path(&filepath).await.unwrap();
            let result =
                upload::upload_object_stream(&client, "test-bucket", stream, &filepath).await;
            print!("{result:?} ... ");
            let attributes = object::get_object_attributes(&client, "test-bucket", &filepath).await;
            println!("{attributes:?}");
        } else {
            println!("<not a file>");
        }
    }
}
