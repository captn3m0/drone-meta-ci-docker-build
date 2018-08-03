import yaml
import copy
import sys
from jinja2 import Template
from collections import defaultdict

rendered_set = set([])
images = None


def rendered(tag):
    return tag in rendered_set


def render_dockerfile(tag, base_image, roles):
    contents = ""

    for role in roles:
        role_file = "roles/{role}/Dockerfile".format(role=role)
        with open(role_file, 'r') as f:
            contents += "# ROLE {role}\n".format(role=role)
            contents += f.read()
            # Put an extra newline at the end of the file
            # so the next role starts from a new line
            contents += "\n"

    with open("Dockerfile.j2", 'r') as f:
        template = Template(f.read())
        final_dockerfile = "{tag}.Dockerfile".format(tag=tag)

        with open(final_dockerfile, 'w') as f:
            f.write(template.render(contents=contents, base_image=base_image))


def render(tag):

    # List of triggers that will flag this image
    # to be rebuild, returned from this method
    dependencies = set([tag])

    image = images[tag]
    base_image = image['base']
    roles = image['roles']

    if ':' not in base_image:
        # Add more dependencies and render the base_image
        dependencies = dependencies.union(render(base_image))
        base_image = "captn3m0/drone-meta-ci-docker-build:{tag}".format(tag=base_image)
    print("Rendering {tag}".format(tag=tag))

    if not rendered(tag):
        render_dockerfile(tag, base_image, roles)
        rendered_set.add(tag)
    return dependencies


with open('config.yml') as fp:
    with open('step.yml') as f:

        images = yaml.load(fp)['images']
        step_template = yaml.load(f)

        drone_pipeline = {}
        environments = defaultdict(lambda: list())

        with open('drone.yml') as f:
            drone_pipeline = yaml.load(f)

        for tag in images:

            step = copy.deepcopy(step_template)
            # First we generate the Dockerfiles
            deps = render(tag)

            for image in deps:
                environments[image].append(tag)
                environments[image] = sorted(environments[image])

            # Then we generate the drone.yml
            step['tags'] = '${{DRONE_COMMIT_BRANCH##master}}{tag}'.format(tag=tag)

            step['dockerfile'] = "{tag}.Dockerfile".format(tag=tag)
            drone_pipeline['pipeline'][tag] = step

        # Only write the drone.yml if no arguments were passed
        if len(sys.argv) == 1:

            print("Rendering .drone.yml")
            for image in environments:
                triggers = environments[image]
                drone_pipeline['pipeline'][image]['when']['environment'] = triggers

            with open('.drone.yml', 'w') as outfile:
                yaml.dump(drone_pipeline, outfile, default_flow_style=False)
