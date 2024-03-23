use uuid::Uuid;

#[tokio::main]
async fn main() {
    let client = ark_s3::new_client();
    let bucket_name = Uuid::now_v7().simple().to_string();
    let create_bucket_result = ark_s3::create_bucket(&client, bucket_name).await;
    println!("{:?}", create_bucket_result);
    let list_buckets_result = ark_s3::list_buckets(&client).await;
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
}
