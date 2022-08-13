from miio import DeviceStatus
from miio.devicestatus import sensor


def test_multiple():
    class MultipleProperties(DeviceStatus):
        @property
        def first(self):
            return "first"

        @property
        def second(self):
            return "second"

    assert (
        repr(MultipleProperties()) == "<MultipleProperties first=first second=second>"
    )


def test_empty():
    class EmptyStatus(DeviceStatus):
        pass

    assert repr(EmptyStatus() == "<EmptyStatus>")


def test_exception():
    class StatusWithException(DeviceStatus):
        @property
        def raise_exception(self):
            raise Exception("test")

    assert (
        repr(StatusWithException()) == "<StatusWithException raise_exception=Exception>"
    )


def test_inheritance():
    class Parent(DeviceStatus):
        @property
        def from_parent(self):
            return True

    class Child(Parent):
        @property
        def from_child(self):
            return True

    assert repr(Child()) == "<Child from_child=True from_parent=True>"


def test_list():
    class List(DeviceStatus):
        @property
        def return_list(self):
            return [0, 1, 2]

    assert repr(List()) == "<List return_list=[0, 1, 2]>"


def test_none():
    class NoneStatus(DeviceStatus):
        @property
        def return_none(self):
            return None

    assert repr(NoneStatus()) == "<NoneStatus return_none=None>"


def test_sensor_decorator():
    class DecoratedProps(DeviceStatus):
        @property
        @sensor(name="Voltage", unit="V", icon="foo")
        def all_kwargs(self):
            pass

        @property
        @sensor(name="Only name")
        def only_name(self):
            pass

        @property
        @sensor(name="", unknown_kwarg="123")
        def unknown(self):
            pass

    status = DecoratedProps()
    sensors = status.sensors()
    assert len(sensors) == 3

    all_kwargs = sensors["all_kwargs"]
    assert all_kwargs.name == "Voltage"
    assert all_kwargs.unit == "V"
    assert all_kwargs.icon == "foo"

    assert sensors["only_name"].name == "Only name"

    assert "unknown_kwarg" in sensors["unknown"].extras
