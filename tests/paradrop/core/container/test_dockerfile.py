from paradrop.core.container.dockerfile import Dockerfile
from paradrop.core.chute.service import Service


def test_get_target_image():
    from paradrop.core.container import dockerfile
    assert dockerfile.get_target_image("go").startswith("golang:")
    assert dockerfile.get_target_image("node").startswith("node:")
    assert dockerfile.get_target_image("python2").startswith("python:2")
    assert dockerfile.get_target_image("python3").startswith("python:3")
    assert dockerfile.get_target_image("unknown").startswith("unknown")


def test_get_target_machine():
    from paradrop.core.container import dockerfile
    result = dockerfile.get_target_machine()
    assert isinstance(result, basestring) and len(result) > 0


def test_getString():
    service = Service(image="python2", command="python")
    dockerfile = Dockerfile(service)
    result = dockerfile.getString()
    assert "FROM" in result
    assert "CMD" in result


def test_isValid():
    # Missing required fields.
    service = Service()
    dockerfile = Dockerfile(service)
    valid, reason = dockerfile.isValid()
    assert valid is False
    assert reason is not None

    # Command is not a string or list.
    service.image = "python2"
    service.command = 42
    dockerfile = Dockerfile(service)
    valid, reason = dockerfile.isValid()
    assert valid is False
    assert reason is not None

    # Valid
    service.command = "python"
    dockerfile = Dockerfile(service)
    valid, reason = dockerfile.isValid()
    assert valid is True
    assert reason is None

    # Packages is not a list.
    service.build['packages'] = 42
    dockerfile = Dockerfile(service)
    valid, reason = dockerfile.isValid()
    assert valid is False
    assert reason is not None

    # Packages contains a weird value.
    service.build['packages'] = ["something\nfunny"]
    dockerfile = Dockerfile(service)
    valid, reason = dockerfile.isValid()
    assert valid is False
    assert reason is not None

    # Valid
    service.build['packages'] = ["a", "ab", "abc"]
    dockerfile = Dockerfile(service)
    valid, reason = dockerfile.isValid()
    assert valid is True
    assert reason is None
