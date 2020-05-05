import pymel.core as pc

from avalon import api


class ConnectFx(api.InventoryAction):

    label = "Connect FX"
    icon = "mouse-pointer"
    color = "#d8d8d8"

    def process(self, containers):
        source_container = pc.PyNode(containers[0]["objectName"])
        target_container = pc.PyNode(containers[1]["objectName"])

        data = {}
        for member in source_container.members(flatten=True):
            if member.nodeType() == "nucleus":
                data["nucleus"] = member

            if not hasattr(member, "cbId"):
                continue

            data[member.cbId.get()] = {"source": member}

        for member in target_container.members():
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
            name=target_container.name() + "_controller"
        )

        controller.addAttr("startFrame")
        attribute = pc.PyNode(controller.name() + ".startFrame")
        attribute.set(channelBox=True)
        attribute >> data["nucleus"].startFrame
        controller.startFrame.set(-10)
        data.pop("nucleus")

        controller.addAttr("blend")
        source_attribute = pc.PyNode(controller.name() + ".blend")
        source_attribute.set(channelBox=True)
        source_attribute.set(keyable=True)

        pc.setKeyframe(
            source_attribute, time=[1], value=1
        )
        pc.setKeyframe(
            source_attribute, time=[-10], value=0
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
