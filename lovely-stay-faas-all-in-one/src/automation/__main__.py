import pulumi
import pulumi_gcp as gcp
from pulumi_gcp import firestore

# https://www.pulumi.com/ai/answers/28Ne4Jw1afiQkS6WqiZbLM/deploying-google-cloud-functions-via-python

database = firestore.Database("bookings-database")

cloud_function = gcp.cloudfunctions.Function(
    "confirm-booking",
    region="europe-west9",
    runtime="python311",
    trigger_http=True,
    source_archive_bucket=gcp.storage.Bucket("source-bucket").name,
    source_archive_object=gcp.storage.BucketObject(
        "source-archive",
        bucket="source-bucket",
        source=pulumi.AssetArchive({".": pulumi.FileArchive("./function_source")})
    ).name,
    entry_point="http_post_bookings",
    environment_variables={
        "DATABASE_ADDRESS": database.urn,
    }
)

pulumi.export("function_url", cloud_function.https_trigger_url)
