import pulumi
import pulumi_docker as docker
import pulumi_random as random
from pulumi_gcp import artifactregistry, firestore, eventarc, workflows
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

# Define a GCP Workflows workflow and add a step to call the POST endpoint

# Read YAML workflow definition from file
with open('booking_confirmation_workflow', 'r') as file:
    workflow_definition = file.read()

# Create a Google Cloud Workflow
booking_confirmation_workflow = workflows.Workflow("my-workflow",
                                                   region=location,
                                                   source_contents=workflow_definition)

# Export the URL of the workflow which can be used to invoke it
pulumi.export("workflow_url", booking_confirmation_workflow.self_link)



# Export the workflow's name and endpoint
pulumi.export("workflow_name", my_workflow.name)
pulumi.export("workflow_endpoint", my_workflow.endpoint)

pulumi.export('trigger', trigger.name)
pulumi.export("url", service.statuses.apply(lambda statuses: statuses[-1].url))
