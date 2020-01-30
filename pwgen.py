import kopf
from kubernetes import client, config
import base64
import secrets


try:
    config.load_incluster_config()
except config.config_exception.ConfigException:
    config.load_kube_config()


def process_spec(spec):
    """
    takes a list of dictonaries, and creates a dictonary with generated secrets, provided secrets,
    or other options the spec provides
    """
    secret_data = {}
    for secret in spec["secretItems"]:
        length = secret.get("length", 25)
        if secret.get("value"):
            secret_data[secret["key"]] = base64.b64encode(
                secret["value"].encode()
            ).decode()
        else:
            secret_data[secret["key"]] = base64.b64encode(
                secrets.token_hex(length).encode()
            ).decode()

    return secret_data


def create_secret(namespace, name, data):
    sec = client.V1Secret()
    sec.metadata = client.V1ObjectMeta(name=name)
    sec.type = "Opaque"
    sec.data = data
    api = client.CoreV1Api()
    try:
        api.create_namespaced_secret(namespace, sec)
    except client.rest.ApiException as e:
        if e.status == 409:
            # TODO what to do when we need to patch. how do we avoid regenerating random strings?
            print("Secret Object Already exists. ")
            # api.patch_namespaced_secret(name, namespace, sec)
        return False

    return True



@kopf.on.create("edu.psu.libraries", "v1alpha1", "pwgens")
def create_fn(body, **kwargs):
    spec = body["spec"]
    name = body["metadata"]["name"]
    namespace = body["metadata"]["namespace"]
    secret_data = process_spec(spec)
    kopf.info(body, reason="SpecProccessed", message="Processed Secret Items")
    create_secret(namespace, name, secret_data)
    kopf.info(body, reason="SecretCreated", message="Created Secret Object")
