import pymel.core as pc

from avalon import api


class ConnectFx(api.InventoryAction):

    label = "Connect FX"
    icon = "mouse-pointer"
    color = "#d8d8d8"

    def get_source_container(self, containers):
        for container in containers:
            members = pc.PyNode(container["objectName"]).members(flatten=True)
            for member in members:
                if member.nodeType() == "nucleus":
                    return container

    def process(self, containers):
        source_container = self.get_source_container(containers)
        source_objectset = pc.PyNode(source_container["objectName"])
        containers.remove(source_container)
        target_objectset = pc.PyNode(containers[0]["objectName"])

        data = {}
        for member in source_objectset.members(flatten=True):
            if member.nodeType() == "nucleus":
                data["nucleus"] = member

            if not hasattr(member, "cbId"):
                continue

            data[member.cbId.get()] = {"source": member}

        msg = "No nucleus was found in {}".format(source_objectset)
        assert "nucleus" in data, msg

        for member in target_objectset.members():
            if member.nodeType() != "transform":
                continue

            shape = member.getShape()
            if not shape:
                continue

            if not hasattr(shape, "cbId"):
                continue

            if shape.cbId.get() not in data:
                continue

            data[shape.cbId.get()].update({"target": shape})

        # Simulation controller.
        controller = pc.spaceLocator(
            name=target_objectset.name() + "_controller"
        )

        controller.addAttr("startFrame")
        attribute = pc.PyNode(controller.name() + ".startFrame")
        attribute.set(channelBox=True)
        attribute >> data["nucleus"].startFrame
        controller.startFrame.set(-20)
        data.pop("nucleus")

        controller.addAttr("blend")
        source_attribute = pc.PyNode(controller.name() + ".blend")
        source_attribute.set(channelBox=True)
        source_attribute.set(keyable=True)

        pc.setKeyframe(
            source_attribute, time=[-10], value=1
        )
        pc.setKeyframe(
            source_attribute, time=[-20], value=0
        )

        for id, nodes in data.iteritems():
            plugs = nodes["source"].listConnections(
                type="blendShape", plugs=True
            )

            plugs.extend(
                nodes["source"].listConnections(
                    type="wrap", plugs=True
                )
            )

            if not plugs:
                continue

            if "target" not in nodes:
                continue

            blendshape = pc.blendShape(
                nodes["target"].getParent(), nodes["source"].getParent()
            )[0]
            attribute_name = nodes["source"].getParent().split(":")[-1]
            target_attribute = pc.PyNode(
                "{}.{}".format(blendshape, attribute_name)
            )
            source_attribute >> target_attribute
