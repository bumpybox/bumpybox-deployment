import pyblish.api


class UpdateFtrackStatus(pyblish.api.InstancePlugin):
    """Create comments in Ftrack."""

    order = pyblish.api.IntegratorOrder
    label = "Update Ftrack Status"
    families = ["render.farm", "renderlayer"]

    def process(self, instance):
        session = instance.context.data["ftrackSession"]

        instance.context.data["ftrackTask"]["status"] = session.query(
            "Status where name is \"{}\"".format("Processing Queued")
        ).one()

        session.commit()
