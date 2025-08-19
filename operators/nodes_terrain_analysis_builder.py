import bpy
import math
from bpy.types import Operator

class TERRAIN_ANALYSIS_OT_build_nodes(Operator):
    """Create material node tree for height, slope, and aspect analysis"""
    bl_idname = "analysis.nodes"
    bl_label = "Terrain Analysis"

    def execute(self, context):
        obj = context.view_layer.objects.active
        if obj is None:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        # Ensure the object has a material slot
        if len(obj.data.materials) == 0:
            obj.data.materials.append(None)  # Add a placeholder material slot

        #######################
        # HEIGHT MATERIAL
        #######################
        heightMatName = 'Height_' + obj.name
        heightMat = bpy.data.materials.get(heightMatName) or bpy.data.materials.new(heightMatName)
        heightMat.use_nodes = True
        heightMat.use_fake_user = True
        obj.data.materials[0] = heightMat  # Assign material to the object

        nt = heightMat.node_tree
        nt.nodes.clear()

        geomNode = nt.nodes.new('ShaderNodeNewGeometry')
        geomNode.location = (-600, 200)
        xyzNode = nt.nodes.new('ShaderNodeSeparateXYZ')
        xyzNode.location = (-400, 200)

        zmin = min([v[2] for v in obj.bound_box])
        zmax = max([v[2] for v in obj.bound_box])

        valNode = nt.nodes.new('ShaderNodeValue')
        valNode.outputs[0].default_value = zmin
        valNode.location = (-600, 0)
        valNode2 = nt.nodes.new('ShaderNodeValue')
        valNode2.outputs[0].default_value = zmax
        valNode2.location = (-600, -100)

        scaleNode = nt.nodes.new('ShaderNodeMapRange')
        scaleNode.location = (-200, 200)
        scaleNode.inputs['To Min'].default_value = 0.0
        scaleNode.inputs['To Max'].default_value = 1.0

        colorRamp = nt.nodes.new('ShaderNodeValToRGB')
        colorRamp.location = (0, 200)
        colorRamp.color_ramp.elements[0].color = (0, 1, 0, 1)
        colorRamp.color_ramp.elements[1].color = (1, 0, 0, 1)

        diffuse = nt.nodes.new('ShaderNodeBsdfDiffuse')
        diffuse.location = (300, 200)
        output = nt.nodes.new('ShaderNodeOutputMaterial')
        output.location = (500, 200)

        links = nt.links
        links.new(geomNode.outputs['Position'], xyzNode.inputs['Vector'])
        links.new(xyzNode.outputs['Z'], scaleNode.inputs['Value'])
        # --- Added connections for value nodes ---
        links.new(valNode.outputs[0], scaleNode.inputs['From Min'])
        links.new(valNode2.outputs[0], scaleNode.inputs['From Max'])
        # -----------------------------------------
        links.new(scaleNode.outputs['Result'], colorRamp.inputs['Fac'])
        links.new(colorRamp.outputs['Color'], diffuse.inputs['Color'])
        links.new(diffuse.outputs['BSDF'], output.inputs['Surface'])

        #######################
        # SLOPE MATERIAL
        #######################
        slopeMatName = 'Slope_' + obj.name
        slopeMat = bpy.data.materials.get(slopeMatName) or bpy.data.materials.new(slopeMatName)
        slopeMat.use_nodes = True
        slopeMat.use_fake_user = True
        obj.data.materials.append(slopeMat)  # Add material slot for slope
        nt = slopeMat.node_tree
        nt.nodes.clear()

        geomNode = nt.nodes.new('ShaderNodeNewGeometry')
        geomNode.location = (-600, 0)
        normalNode = geomNode

        separate = nt.nodes.new('ShaderNodeSeparateXYZ')
        separate.location = (-400, 0)
        links.new(normalNode.outputs['True Normal'], separate.inputs['Vector'])

        acosNode = nt.nodes.new('ShaderNodeMath')
        acosNode.operation = 'ARCCOSINE'
        acosNode.location = (-200, 0)
        links.new(separate.outputs['Z'], acosNode.inputs[0])

        rad2deg = nt.nodes.new('ShaderNodeMath')
        rad2deg.operation = 'MULTIPLY'
        rad2deg.inputs[1].default_value = 180 / math.pi
        rad2deg.location = (0, 0)
        links.new(acosNode.outputs[0], rad2deg.inputs[0])

        colorRamp = nt.nodes.new('ShaderNodeValToRGB')
        colorRamp.location = (200, 0)
        colorRamp.color_ramp.elements[0].color = (0, 1, 0, 1)
        colorRamp.color_ramp.elements[1].color = (1, 0, 0, 1)

        diffuse = nt.nodes.new('ShaderNodeBsdfDiffuse')
        diffuse.location = (400, 0)
        output = nt.nodes.new('ShaderNodeOutputMaterial')
        output.location = (600, 0)

        links.new(rad2deg.outputs[0], colorRamp.inputs['Fac'])
        links.new(colorRamp.outputs['Color'], diffuse.inputs['Color'])
        links.new(diffuse.outputs['BSDF'], output.inputs['Surface'])

        #######################
        # ASPECT MATERIAL
        #######################
        aspectMatName = 'Aspect_' + obj.name
        aspectMat = bpy.data.materials.get(aspectMatName) or bpy.data.materials.new(aspectMatName)
        aspectMat.use_nodes = True
        aspectMat.use_fake_user = True
        obj.data.materials.append(aspectMat)  # Add material slot for aspect
        nt = aspectMat.node_tree
        nt.nodes.clear()

        geomNode = nt.nodes.new('ShaderNodeNewGeometry')
        geomNode.location = (-600, 0)
        separate = nt.nodes.new('ShaderNodeSeparateXYZ')
        separate.location = (-400, 0)
        links.new(geomNode.outputs['True Normal'], separate.inputs['Vector'])

        atan2 = nt.nodes.new('ShaderNodeMath')
        atan2.operation = 'ARCTAN2'
        atan2.location = (-200, 0)
        links.new(separate.outputs['Y'], atan2.inputs[0])
        links.new(separate.outputs['X'], atan2.inputs[1])

        rad2deg = nt.nodes.new('ShaderNodeMath')
        rad2deg.operation = 'MULTIPLY'
        rad2deg.inputs[1].default_value = 180 / math.pi
        rad2deg.location = (0, 0)
        links.new(atan2.outputs[0], rad2deg.inputs[0])

        colorRamp = nt.nodes.new('ShaderNodeValToRGB')
        colorRamp.location = (200, 0)
        colorRamp.color_ramp.elements[0].color = (0, 1, 0, 1)
        colorRamp.color_ramp.elements[1].color = (1, 0, 0, 1)

        diffuse = nt.nodes.new('ShaderNodeBsdfDiffuse')
        diffuse.location = (400, 0)
        output = nt.nodes.new('ShaderNodeOutputMaterial')
        output.location = (600, 0)

        links.new(rad2deg.outputs[0], colorRamp.inputs['Fac'])
        links.new(colorRamp.outputs['Color'], diffuse.inputs['Color'])
        links.new(diffuse.outputs['BSDF'], output.inputs['Surface'])

        return {'FINISHED'}


# ---------------------------
# Registration
# ---------------------------
classes = [TERRAIN_ANALYSIS_OT_build_nodes]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
