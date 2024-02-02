import pulumi
import pulumi_docker as docker
import pulumi_random as random
from pulumi_gcp import artifactregistry, firestore, eventarc, pubsub, cloudfunctions, storage, serviceaccount
from pulumi_gcp import cloudrun

# Import the program's configuration settings.
config = pulumi.Config()
app_path = config.get("appPath", "./app")
image_name = config.get("imageName", "my-app")
container_port = config.get_int("containerPort", 8080)
cpu = config.get_int("cpu", 1)
memory = config.get("memory", "1Gi")
concurrency = config.get_float("concurrency", 50)

# Import the provider's configuration settings.
gcp_config = pulumi.Config("gcp")
location = gcp_config.require("region")
project = gcp_config.require("project")

# Create a unique Artifact Registry repository ID
unique_string = random.RandomString(
    "unique-string",
    length=4,
    lower=True,
    upper=False,
    numeric=True,
    special=False,
)
repo_id = pulumi.Output.concat(
    "repo-",
    unique_string.result
)

# Create an Artifact Registry repository
repository = artifactregistry.Repository(
    "repository",
    description="Repository for container image",
    format="DOCKER",
    location=location,
    repository_id=repo_id,
)

# Form the repository URL
repo_url = pulumi.Output.concat(
    location,
    "-docker.pkg.dev/",
    project,
    "/",
    repository.repository_id
)

# Create a container image for the service.
# Before running `pulumi up`, configure Docker for Artifact Registry authentication
# as described here: https://cloud.google.com/artifact-registry/docs/docker/authentication
image = docker.Image(
    "image",
    image_name=pulumi.Output.concat(repo_url, "/", image_name),
    build=docker.DockerBuildArgs(
        context=app_path,
        # Cloud Run currently requires x86_64 images
        # https://cloud.google.com/run/docs/container-contract#languages
        platform="linux/amd64"
    ),
)

database = firestore.Database("bookings-database")

# Create a Cloud Run service definition.
service = cloudrun.Service(
    "service",
    cloudrun.ServiceArgs(
        location=location,
        template=cloudrun.ServiceTemplateArgs(
            spec=cloudrun.ServiceTemplateSpecArgs(
                containers=[
                    cloudrun.ServiceTemplateSpecContainerArgs(
                        image=image.repo_digest,
                        resources=cloudrun.ServiceTemplateSpecContainerResourcesArgs(
                            limits=dict(
                                memory=memory,
                                cpu=cpu,
                            ),
                        ),
                        ports=[
                            cloudrun.ServiceTemplateSpecContainerPortArgs(
                                container_port=container_port,
                            ),
                        ],
                        envs=[
                            cloudrun.ServiceTemplateSpecContainerEnvArgs(
                                name="FLASK_RUN_PORT",
                                value=container_port,
                            ),
                            cloudrun.ServiceTemplateSpecContainerEnvArgs(
                                name="DATABASE_ADDRESS",
                                value=database.urn,
                            ),
                        ],
                    ),
                ],
                container_concurrency=concurrency,
            ),
        ),
    ),
)

# Create an IAM member to make the service publicly accessible.
invoker = cloudrun.IamMember(
    "invoker",
    cloudrun.IamMemberArgs(
        location=location,
        service=service.name,
        role="roles/run.invoker",
        member="allUsers",
    ),
)

# Set up Eventarc Trigger
trigger = eventarc.Trigger('booking-confirmed-trigger',
                           location=location,
                           destination={
                               "cloudRunService": {
                                   "service": service.name,
                                   "path": "/gateway/mail/booking-confirmed",
                                   "region": service.location
                               }},
                           matching_criterias=[{
                               "attribute": "type",
                               "value": "google.cloud.firestore.document.v1.created"
                           }])

pulumi.export('trigger', trigger.name)
pulumi.export("url", service.statuses.apply(lambda statuses: statuses[-1].url))

# Create a Firestore database instance
firestore_db = firestore.Database("firestore-db", location_id="global")

# Deploy the Pub/Sub Topic for offers
offers_topic = pubsub.Topic("offers-topic")

# Deploy the Cloud Function that subscribes to the Pub/Sub topic
offers_integration_function = cloudfunctions.Function(
    "offers-integration-function",
    runtime="python311",
    available_memory_mb=128,
    source_archive_bucket=storage.Bucket("source-bucket").name,
    source_archive_object=storage.BucketObject(
        "source-object",
        bucket=storage.Bucket("source-bucket").name,
        source=pulumi.asset.FileArchive(
            "./offers-integration-function")
    ).name,
    entry_point="handler",
    event_trigger=cloudfunctions.FunctionEventTriggerArgs(
        event_type="google.pubsub.topic.publish",
        resource=offers_topic.id,
    )
)

# Setup IAM for the Cloud Function to access Firestore
firestore_access_member = serviceaccount.IAMMember(
    "firestore-access-member",
    service_account_id=offers_integration_function.service_account_email,
    role="roles/datastore.user",
    member=pulumi.Output.concat("serviceAccount:",
                                offers_integration_function.service_account_email),
)

# Deploy the Cloud Run service
cloud_run_service = cloudrun.Service("cloud-run-service",
                                     location="us-central1",
                                     template=gcp.cloudrun.ServiceTemplateArgs(
                                         spec=gcp.cloudrun.ServiceTemplateSpecArgs(
                                             containers=[gcp.cloudrun.ServiceTemplateSpecContainerArgs(
                                                 image="gcr.io/my-project/my-image:latest",
                                                 envs=[gcp.cloudrun.ServiceTemplateSpecContainerEnvArgs(
                                                     name="FIRESTORE_DATABASE",
                                                     value=firestore_db.name,
                                                 )],
                                             )],
                                         ),
                                     ),
                                     traffics=[gcp.cloudrun.ServiceTrafficArgs(
                                         percent=100,
                                         latest_revision=True,
                                     )],
                                     )

# Grant permissions for the service to access Firestore
cloud_run_service_account = gcp.serviceaccount.Account("cloud-run-service-account",
                                                       account_id="cloud-run-service-account",
                                                       display_name="Cloud Run service account",
                                                       )
cloud_run_iam = gcp.serviceaccount.IAMMember("cloud-run-iam",
                                             service_account_id=cloud_run_service_account.name,
                                             role="roles/datastore.user",
                                             member=pulumi.Output.concat("serviceAccount:",
                                                                         cloud_run_service_account.email),
                                             )

# Export the URLs of the cloud service and function
pulumi.export("cloud_function_url", offers_integration_function.https_trigger_url)
pulumi.export("cloud_run_service_url", cloud_run_service.statuses[0].url)
