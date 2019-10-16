import os
import maya.OpenMaya as om
import maya.OpenMayaMPx as ommpx
import maya.OpenMayaAnim as omAnim
import maya.cmds as cmds
import pymel.core as pm


class CarpetRoll(ommpx.MPxDeformerNode):

    TYPE_NAME = "CarpetRoll"
    TYPE_ID = om.MTypeId(0x0007F7FC)

    def __init__(self):
        ommpx.MPxDeformerNode.__init__(self)
        self.subd_width, self.subd_height = 0, 0

    def deform(self, data_block, geo_iter, matrix, multi_index):
        geo_iter.reset()
        selection = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(selection)
        m_iter = om.MItSelectionList(selection, om.MFn.kTransform)

        while not m_iter.isDone():
            mobject = om.MObject()
            dp = om.MDagPath()
            m_iter.getDagPath(dp, mobject)
            unsigned_int_ptr = om.uIntPtr()
            dp.numberOfShapesDirectlyBelow(unsigned_int_ptr)
            if unsigned_int_ptr.value() < 2:
                m_iter.next()
                continue
            dp.extendToShapeDirectlyBelow(1)
            polymesh = om.MFnDependencyNode(dp.node())
            poly_plug = polymesh.findPlug("inMesh")
            connect_plug = om.MPlugArray()
            poly_plug.connectedTo(connect_plug, True, False)
            src_plug = connect_plug[0]
            poly_planer_node = src_plug.node()
            poly_plane_fn = om.MFnDependencyNode(poly_planer_node)
            om.MGlobal.displayInfo(poly_plane_fn.name())
            self.subd_width = poly_plane_fn.findPlug("subdivisionsWidth").asInt()
            self.subd_height = poly_plane_fn.findPlug("subdivisionsHeight").asInt()
            m_iter.next()

        last_20_points = {}
        while not geo_iter.isDone():
            last_20_points[geo_iter.index()] = geo_iter.position()
            if geo_iter.index() % self.subd_height == 0:
                pt = geo_iter.position()
                # om.MGlobal.select()
                current_time = int(omAnim.MAnimControl_currentTime().value())
                pt.y += 0.2 * current_time
                geo_iter.setPosition(pt)
                last_20_points = dict()
            geo_iter.next()

    @classmethod
    def creator(cls):
        return CarpetRoll()

    @classmethod
    def initialize(cls):
        pass


def initializePlugin(plugin):
    vendor = "AJ"
    version = "b.1.0.0"

    plugin_fn = ommpx.MFnPlugin(plugin, vendor, version)

    try:
        plugin_fn.registerNode(CarpetRoll.TYPE_NAME, CarpetRoll.TYPE_ID,
                               CarpetRoll.creator, CarpetRoll.initialize,
                               ommpx.MPxNode.kDeformerNode)
    except:
        pm.displayError("Failed to register node {0}".format(
            CarpetRoll.TYPE_NAME))


def uninitializePlugin(plugin):

    plugin_fn = ommpx.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterNode(CarpetRoll.TYPE_ID)
    except:
        pm.displayError("Failed to deregister node {0}".format(
            CarpetRoll.TYPE_NAME))


if __name__ == "__main__":

    pm.newFile(f=1)
    plugin_name = "E:/Maya/MayaAPI/Deforner/CarpetRoll.py"
    if pm.pluginInfo(plugin_name, q=1, loaded=True):
        pm.unloadPlugin(os.path.basename(plugin_name), f=True)
    pm.loadPlugin(plugin_name)
    pplane_transform, pplane_shape = pm.polyPlane()
    pplane_shape.subdivisionsWidth.set(20)
    pplane_shape.subdivisionsHeight.set(20)
    pm.select(pplane_transform)
    pm.deformer(type="CarpetRoll")
