#
#
# This Blender add-on assigns one or more Bezier Curves as shape keys to another 
# Bezier Curve
#
# Supported Blender Version: 2.8 Beta
#
# Copyright (C) 2019  Shrinivas Kulkarni
#
# License: MIT (https://github.com/Shriinivas/assignshapekey/blob/master/LICENSE)
#
# Not yet pep8 compliant 

import bpy, math
from bpy.props import BoolProperty, EnumProperty
from collections import OrderedDict
from mathutils import Vector
from math import sqrt
from functools import cmp_to_key

#################### UI and Registration Stuff ####################

bl_info = {
    "name": "Assign Shape Keys",
    "category": "Animation",
    "blender": (2, 80, 0),
}

noneStr = "-None-"
CURVE_NAME_PREFIX = 'Curve'

#TODO: Replace with a simple checkbox
def getAlignmentList(scene, context):
    return [(noneStr, 'No Alignment', "Don' align the curve segments"), \
        ('vertCo', 'Vertex Coordinates', 
            'Align the curve segments based on vertex coordinates')]

matchList = [('vCnt', 'Vertex Count', 'Match by vertex count'),
            ('bbArea', 'Area', 'Match by surface area of the bounding box'), \
            ('bbHeight', 'Height', 'Match by bounding box height'), \
            ('bbWidth', 'Width', 'Match by bounding box width'),
            ('bbDepth', 'Depth', 'Match by bounding box depth'),
            ('minX', 'Min X', 'Match by  bounding bon Min X'), 
            ('maxX', 'Max X', 'Match by  bounding bon Max X'),
            ('minY', 'Min Y', 'Match by  bounding bon Min Y'), 
            ('maxY', 'Max Y', 'Match by  bounding bon Max Y'),
            ('minZ', 'Min Z', 'Match by  bounding bon Min Z'), 
            ('maxZ', 'Max Z', 'Match by  bounding bon Max Z')]
    
class AssignShapeKeyParams(bpy.types.PropertyGroup):
    
    removeOriginal : BoolProperty(name="Remove Original Curves", \
        description="Replace with the original target and shape key curves with the new ones", \
            default = False)
    
    space : EnumProperty(name="Space", items = [('worldspace', 'World Space', 'worldspace'), 
        ('localspace', 'Local Space', 'localspace')], \
        description = 'Space that shape keys are evluated in')

    alignList : EnumProperty(name="Vertex Alignment", items = getAlignmentList, \
        description = 'Start aligning the vertices of target and shape keys from')
    
    alignVal1 : EnumProperty(name="Value 1", 
        items = matchList, default = 'minX', description='First align criterion')

    alignVal2 : EnumProperty(name="Value 2", 
        items = matchList, default = 'maxY', description='Second align criterion')

    alignVal3 : EnumProperty(name="Value 3", 
        items = matchList, default = 'minZ', description='Third align criterion')
    
    matchParts : BoolProperty(name="Match Parts", \
        description='Match disconnected parts', default = False)
        
    matchCri1 : EnumProperty(name="Value 1", 
        items = matchList, default = 'minX', description='First match criterion')

    matchCri2 : EnumProperty(name="Value 2", 
        items = matchList, default = 'maxY', description='Second match criterion')

    matchCri3 : EnumProperty(name="Value 3", 
        items = matchList, default = 'minZ', description='Third match criterion')
    
class AssignShapeKeysPanel(bpy.types.Panel):
    
    bl_label = "Assign Shape Keys"
    bl_idname = "panel.assign_shape_keys"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = '.objectmode'
        
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        
        row = col.row()
        row.prop(context.window_manager.AssignShapeKeyParams, "removeOriginal")

        row = col.row()
        row.prop(context.window_manager.AssignShapeKeyParams, "space")

        row = col.row()
        row.prop(context.window_manager.AssignShapeKeyParams, "alignList")
        
        if(context.window_manager.AssignShapeKeyParams.alignList == 'vertCo'):
            row = col.row()
            row.prop(context.window_manager.AssignShapeKeyParams, "alignVal1")
            row.prop(context.window_manager.AssignShapeKeyParams, "alignVal2")
            row.prop(context.window_manager.AssignShapeKeyParams, "alignVal3")
        
        row = col.row()
        row.prop(context.window_manager.AssignShapeKeyParams, "matchParts")
        
        if(context.window_manager.AssignShapeKeyParams.matchParts):
            row = col.row()
            row.prop(context.window_manager.AssignShapeKeyParams, "matchCri1")
            row.prop(context.window_manager.AssignShapeKeyParams, "matchCri2")
            row.prop(context.window_manager.AssignShapeKeyParams, "matchCri3")
        
        row = col.row()
        row.operator("object.assign_shape_keys")

class AssignShapeKeysOp(bpy.types.Operator):

    bl_idname = "object.assign_shape_keys"
    bl_label = "Assign Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        removeOriginal = context.window_manager.AssignShapeKeyParams.removeOriginal
        space = context.window_manager.AssignShapeKeyParams.space

        matchParts = context.window_manager.AssignShapeKeyParams.matchParts
        matchCri1 = context.window_manager.AssignShapeKeyParams.matchCri1
        matchCri2 = context.window_manager.AssignShapeKeyParams.matchCri2
        matchCri3 = context.window_manager.AssignShapeKeyParams.matchCri3

        alignBy = context.window_manager.AssignShapeKeyParams.alignList
        alignVal1 = context.window_manager.AssignShapeKeyParams.alignVal1
        alignVal2 = context.window_manager.AssignShapeKeyParams.alignVal2
        alignVal3 = context.window_manager.AssignShapeKeyParams.alignVal3

        createdObjsMap = main(removeOriginal, space, \
                            matchParts, [matchCri1, matchCri2, matchCri3], \
                                alignBy, [alignVal1, alignVal2, alignVal3])

        return {'FINISHED'}

def register():
    bpy.utils.register_class(AssignShapeKeysPanel)
    bpy.utils.register_class(AssignShapeKeysOp)
    bpy.utils.register_class(AssignShapeKeyParams)
    bpy.types.WindowManager.AssignShapeKeyParams = \
        bpy.props.PointerProperty(type=AssignShapeKeyParams)

def unregister():
    bpy.utils.unregister_class(AssignShapeKeysOp)
    bpy.utils.unregister_class(AssignShapeKeysPanel)
    del bpy.types.WindowManager.AssignShapeKeyParams
    bpy.utils.unregister_class(AssignShapeKeyParams)

if __name__ == "__main__":
    register()

###################### addon code start ####################

DEF_ERR_MARGIN = 0.0001

class Segment():

    #From svgpathtools
    #pts[0] - start, pts[1] - ctrl1, pts[2] - ctrl2, , pts[3] - end
    def pointAtT(pts, t):
        return pts[0] + t * (3 * (pts[1] - pts[0]) + 
            t* (3 * (pts[0] + pts[2]) - 6 * pts[1] + 
                t * (-pts[0] + 3 * (pts[1] - pts[2]) + pts[3])))

    #From svgpathtools (static method)
    def getSegLenRecurs(pts, start, end, t1 = 0, t2 = 1, error = DEF_ERR_MARGIN):
        t1_5 = (t1 + t2)/2
        mid = Segment.pointAtT(pts, t1_5)
        l = (end - start).length
        l2 = (mid - start).length + (end - mid).length
        if (l2 - l > error):
            return (Segment.getSegLenRecurs(pts, start, mid, t1, t1_5, error) +
                    Segment.getSegLenRecurs(pts, mid, end, t1_5, t2, error))
        return l2

    def __init__(self, start, ctrl1, ctrl2, end):
        self.start = start
        self.ctrl1 = ctrl1
        self.ctrl2 = ctrl2
        self.end = end
        pts = [start, ctrl1, ctrl2, end]
        self.length = Segment.getSegLenRecurs(pts, start, end)

    #see https://stackoverflow.com/questions/878862/drawing-part-of-a-b%c3%a9zier-curve-by-reusing-a-basic-b%c3%a9zier-curve-function/879213#879213
    def partialSeg(self, t0, t1):    
        pts = [self.start, self.ctrl1, self.ctrl2, self.end]

        if(t0 > t1):
            tt = t1
            t1 = t0
            t0 = tt

        #Let's make at least the line segments of predictable length :)
        if(pts[0] == pts[1] and pts[2] == pts[3]):
            pt0 = Vector([(1 - t0) * pts[0][i] + t0 * pts[2][i] for i in range(0, 3)])
            pt1 = Vector([(1 - t1) * pts[0][i] + t1 * pts[2][i] for i in range(0, 3)])
            return Segment(pt0, pt0, pt1, pt1)

        u0 = 1.0 - t0
        u1 = 1.0 - t1

        qa = [pts[0][i]*u0*u0 + pts[1][i]*2*t0*u0 + pts[2][i]*t0*t0 for i in range(0, 3)]
        qb = [pts[0][i]*u1*u1 + pts[1][i]*2*t1*u1 + pts[2][i]*t1*t1 for i in range(0, 3)]
        qc = [pts[1][i]*u0*u0 + pts[2][i]*2*t0*u0 + pts[3][i]*t0*t0 for i in range(0, 3)]
        qd = [pts[1][i]*u1*u1 + pts[2][i]*2*t1*u1 + pts[3][i]*t1*t1 for i in range(0, 3)]

        pta = Vector([qa[i]*u0 + qc[i]*t0 for i in range(0, 3)])
        ptb = Vector([qa[i]*u1 + qc[i]*t1 for i in range(0, 3)])
        ptc = Vector([qb[i]*u0 + qd[i]*t0 for i in range(0, 3)])
        ptd = Vector([qb[i]*u1 + qd[i]*t1 for i in range(0, 3)])

        return Segment(pta, ptb, ptc, ptd)

    #see https://stackoverflow.com/questions/24809978/calculating-the-bounding-box-of-cubic-bezier-curve
    #(3 D - 9 C + 9 B - 3 A) t^2 + (6 A - 12 B + 6 C) t + 3 (B - A)
    #pts[0] - start, pts[1] - ctrl1, pts[2] - ctrl2, , pts[3] - end
    #TODO: Return Vectors to make world space calculations consistent
    def bbox(self, mw = None):
        def evalBez(AA, BB, CC, DD, t):
            return AA * (1 - t) * (1 - t) * (1 - t) + \
                    3 * BB * t * (1 - t) * (1 - t) + \
                        3 * CC * t * t * (1 - t) + \
                            DD * t * t * t

        A = self.start
        B = self.ctrl1
        C = self.ctrl2
        D = self.end

        if(mw != None):
            A = mw @ A
            B = mw @ B
            C = mw @ C
            D = mw @ D

        MINXYZ = [min([A[i], D[i]]) for i in range(0, 3)]
        MAXXYZ = [max([A[i], D[i]]) for i in range(0, 3)]
        leftBotBack_rgtTopFront = [MINXYZ, MAXXYZ]

        a = [3 * D[i] - 9 * C[i] + 9 * B[i] - 3 * A[i] for i in range(0, 3)]
        b = [6 * A[i] - 12 * B[i] + 6 * C[i] for i in range(0, 3)]
        c = [3 * (B[i] - A[i]) for i in range(0, 3)]

        solnsxyz = []
        for i in range(0, 3):
            solns = []
            if(a[i] == 0):
                if(b[i] == 0):
                    solns.append(0)#Independent of t so lets take the starting pt
                else:
                    solns.append(c[i] / b[i])
            else:
                rootFact = b[i] * b[i] - 4 * a[i] * c[i]
                if(rootFact >=0 ):
                    #Two solutions with + and - sqrt
                    solns.append((-b[i] + sqrt(rootFact)) / (2 * a[i]))
                    solns.append((-b[i] - sqrt(rootFact)) / (2 * a[i]))
            solnsxyz.append(solns)
        
        for i, soln in enumerate(solnsxyz):
            for j, t in enumerate(soln):
                if(t < 1 and t > 0):                
                    co = evalBez(A[i], B[i], C[i], D[i], t)
                    if(co < leftBotBack_rgtTopFront[0][i]):
                        leftBotBack_rgtTopFront[0][i] = co
                    if(co > leftBotBack_rgtTopFront[1][i]):
                        leftBotBack_rgtTopFront[1][i] = co 
                                           
        return leftBotBack_rgtTopFront

class Part():
    def __init__(self, parent, segs, isClosed):
        self.parent = parent
        self.segs = segs

        #use_cyclic_u
        self.isClosed = isClosed 

        #Should this be closed based on its counterparts in other paths
        self.toClose = isClosed 

        self.length = sum(seg.length for seg in self.segs)
        self.bbox = None
        self.bboxWorldSpace = None
            
    def getSeg(self, idx):
        return self.segs[idx]
        
    def getSegs(self):
        return self.segs
        
    def getSegsCopy(self, start, end):
        if(start == None):
            start = 0
        if(end == None):
            end = len(self.segs)
        return self.segs[start:end]

    def getBBox(self, worldSpace):
        #Avoid frequent calculations, as this will be called in compare method
        if(not worldSpace and self.bbox != None):
            return self.bbox
            
        if(worldSpace and self.bboxWorldSpace != None):
            return self.bboxWorldSpace
            
        leftBotBack_rgtTopFront = [[None]*3,[None]*3] 

        for seg in self.segs:

            if(worldSpace):
                bb = seg.bbox(self.parent.curve.matrix_world)
            else:
                bb = seg.bbox()

            for i in range(0, 3):                
                if (leftBotBack_rgtTopFront[0][i] == None or \
                    bb[0][i] < leftBotBack_rgtTopFront[0][i]):
                    leftBotBack_rgtTopFront[0][i] = bb[0][i]

            for i in range(0, 3):
                if (leftBotBack_rgtTopFront[1][i] == None or \
                    bb[1][i] > leftBotBack_rgtTopFront[1][i]):
                    leftBotBack_rgtTopFront[1][i] = bb[1][i]
                    
        if(worldSpace):
            self.bboxWorldSpace = leftBotBack_rgtTopFront
        else:
            self.bbox = leftBotBack_rgtTopFront
            
        return leftBotBack_rgtTopFront

    #private
    def getBBDiff(self, axisIdx, worldSpace):
        obj = self.parent.curve
        bbox = self.getBBox(worldSpace)
        diff = abs(bbox[1][axisIdx] - bbox[0][axisIdx])        
        return diff
        
    def getBBWidth(self, worldSpace):
        return self.getBBDiff(0, worldSpace)
        
    def getBBHeight(self, worldSpace):
        return self.getBBDiff(1, worldSpace)
        
    def getBBDepth(self, worldSpace):
        return self.getBBDiff(2, worldSpace)
        
    def bboxSurfaceArea(self, worldSpace):    
        leftBotBack_rgtTopFront = self.getBBox(worldSpace)
        w = abs( leftBotBack_rgtTopFront[1][0] - leftBotBack_rgtTopFront[0][0] )
        l = abs( leftBotBack_rgtTopFront[1][1] - leftBotBack_rgtTopFront[0][1] )
        d = abs( leftBotBack_rgtTopFront[1][2] - leftBotBack_rgtTopFront[0][2] )
    
        return 2 * (w * l + w * d + l * d)
        
    def getSegCnt(self):
        return len(self.segs)

    def __repr__(self):
        return str(self.length)


class Path:
    def __init__(self, curve, objData = None, name = None):
        
        if(objData == None):
            objData = curve.data
            
        if(name == None):
            name = curve.name
        
        self.name = name
        self.curve = curve
        
        self.parts = [Part(self, getSplineSegs(s), s.use_cyclic_u) for s in objData.splines]

    def getPartCnt(self):
        return len(self.parts)
        
    def getPartView(self):
        p = Part(self, [seg for part in self.parts for seg in part.getSegs()], None)
        return p
    
    def getPartBoundaryIdxs(self):
        cumulCntList = set()
        cumulCnt = 0
        
        for p in self.parts:
            cumulCnt += p.getSegCnt()
            cumulCntList.add(cumulCnt)
            
        return cumulCntList
        
    def updatePartsList(self, segCntsPerPart, byPart):
        monolithicSegList = [seg for part in self.parts for seg in part.getSegs()]
        oldParts = self.parts[:]
        currPart = oldParts[0]
        partIdx = 0
        self.parts.clear()

        for i in range(0, len(segCntsPerPart)):
            if( i == 0):
                currIdx = 0
            else:
                currIdx = segCntsPerPart[i-1]

            nextIdx = segCntsPerPart[i]
            isClosed = False

            if(vectCmpWithMargin(monolithicSegList[currIdx].start, currPart.getSegs()[0].start) and \
                vectCmpWithMargin(monolithicSegList[nextIdx-1].end, currPart.getSegs()[-1].end)):
                isClosed = currPart.isClosed 

            self.parts.append(Part(self, monolithicSegList[currIdx:nextIdx], isClosed))
            if(monolithicSegList[nextIdx-1] == currPart.getSegs()[-1]):
                partIdx += 1
                if(partIdx < len(oldParts)):
                    currPart = oldParts[partIdx]

def main(removeOriginal, space, matchParts, matchCriteria, alignBy, alignValues):
    targetObj = bpy.context.active_object
    if(targetObj == None or not isBezier(targetObj)):
        return

    target = Path(targetObj)
    
    shapekeys = [Path(c) for c in bpy.context.selected_objects if isBezier(c) \
        and c != bpy.context.active_object]

    if(len(shapekeys) == 0):
        return

    shapekeys = getExistingShapeKeyPaths(target) + shapekeys
    userSel = [target] + shapekeys

    for path in userSel:
        alignPath(path, matchParts, matchCriteria, alignBy, alignValues)

    addMissingSegs(userSel, byPart = matchParts)

    bIdxs = set()
    for path in userSel:
        bIdxs = bIdxs.union(path.getPartBoundaryIdxs())

    for path in userSel:
        path.updatePartsList(sorted(list(bIdxs)), byPart = False)

    #All will have same part count by now        
    allToClose = [all(path.parts[j].isClosed for path in userSel) 
        for j in range(0, len(userSel[0].parts))]

    #All paths will have the same no of splines with the same no of bezier points
    for path in userSel:
        for j, part in enumerate(path.parts):
            part.toClose = allToClose[j]

    curve = addCurve(target)

    curve.shape_key_add(name = 'Basis')

    addShapeKey(curve, shapekeys, space)

    if(removeOriginal):
        for path in userSel:
            safeRemoveCurveObj(path.curve)

    return {}

def isBezier(obj):
    return obj.type == 'CURVE' and len(obj.data.splines) > 0 \
        and obj.data.splines[0].type == 'BEZIER'

def getSplineSegs(spline):
    p = spline.bezier_points
    segs = [Segment(p[i-1].co, p[i-1].handle_right, p[i].handle_left, p[i].co) \
        for i in range(1, len(p))]
    if(spline.use_cyclic_u):
        segs.append(Segment(p[-1].co, p[-1].handle_right, p[0].handle_left, p[0].co))
    return segs
    
#Avoid errors due to floating point conversions/comparisons
#TODO: return -1, 0, 1
def floatCmpWithMargin(float1, float2, margin = DEF_ERR_MARGIN):
    return abs(float1 - float2) < margin 

def vectCmpWithMargin(v1, v2, margin = DEF_ERR_MARGIN):
    return all(floatCmpWithMargin(v1[i], v2[i]) for i in range(0, len(v1)))


def subdivideSeg(origSeg, noSegs):
    if(noSegs < 2):
        return [origSeg]
        
    segs = []
    oldT = 0
    segLen = origSeg.length / noSegs
    
    for i in range(0, noSegs-1):
        t = float(i+1) / noSegs
        seg = origSeg.partialSeg(oldT, t)
        segs.append(seg)
        oldT = t
    
    seg = origSeg.partialSeg(oldT, 1)
    segs.append(seg)
    
    return segs
    

def getSubdivCntPerSeg(part, toAddCnt):
    
    class SegWrapper:
        def __init__(self, idx, seg):
            self.idx = idx
            self.seg = seg
            self.length = seg.length
        
    class PartWrapper:
        def __init__(self, part):
            self.segList = []
            self.segCnt = len(part.getSegs())
            for idx, seg in enumerate(part.getSegs()):
                self.segList.append(SegWrapper(idx, seg))
        
    partWrapper = PartWrapper(part)
    partLen = part.length
    avgLen = partLen / (partWrapper.segCnt + toAddCnt)

    segsToDivide = [sr for sr in partWrapper.segList if sr.seg.length >= avgLen]
    segToDivideCnt = len(segsToDivide)
    avgLen = sum(sr.seg.length for sr in segsToDivide) / (segToDivideCnt + toAddCnt)

    segsToDivide = sorted(segsToDivide, key=lambda x: x.length, reverse = True)

    cnts = [0] * partWrapper.segCnt
    addedCnt = 0
    
    
    for i in range(0, segToDivideCnt):
        segLen = segsToDivide[i].seg.length

        divideCnt = int(round(segLen/avgLen)) - 1
        if(divideCnt == 0):
            break
            
        if((addedCnt + divideCnt) >= toAddCnt):
            cnts[segsToDivide[i].idx] = toAddCnt - addedCnt
            addedCnt = toAddCnt
            break

        cnts[segsToDivide[i].idx] = divideCnt

        addedCnt += divideCnt
        
    #TODO: Verify if needed
    while(toAddCnt > addedCnt):
        for i in range(0, segToDivideCnt):
            cnts[segsToDivide[i].idx] += 1
            addedCnt += 1
            if(toAddCnt == addedCnt):
                break
                
    return cnts

#Distribute equally; this is likely a rare condition. So why complicate?
def distributeCnt(maxSegCntsByPart, startIdx, extraCnt):    
    added = 0
    elemCnt = len(maxSegCntsByPart) - startIdx
    cntPerElem = math.floor(extraCnt / elemCnt)
    remainder = extraCnt % elemCnt
    
    for i in range(startIdx, len(maxSegCntsByPart)):
        maxSegCntsByPart[i] += cntPerElem
        if(i < remainder + startIdx):
            maxSegCntsByPart[i] += 1

#Make all the paths to have the maximum number of segments in the set
def addMissingSegs(selPaths, byPart):    
    maxSegCntsByPart = []
    maxSegCnt = 0
    
    resSegCnt = []
    sortedPaths = sorted(selPaths, key = lambda c: -len(c.parts))
    
    for i, path in enumerate(sortedPaths):
        if(byPart == False):
            segCnt = path.getPartView().getSegCnt()
            if(segCnt > maxSegCnt):
                maxSegCnt = segCnt
        else:
            resSegCnt.append([])                        
            for j, part in enumerate(path.parts):
                partSegCnt = part.getSegCnt()
                resSegCnt[i].append(partSegCnt)
                
                #First path                 
                if(j == len(maxSegCntsByPart)):
                    maxSegCntsByPart.append(partSegCnt)
                    
                #last part of this path, but other paths in set have more parts
                elif((j == len(path.parts) - 1) and 
                    len(maxSegCntsByPart) > len(path.parts)):
                        
                    remainingSegs = sum(maxSegCntsByPart[j:])
                    if(partSegCnt <= remainingSegs):
                        resSegCnt[i][j] = remainingSegs
                    else:
                        #This part has more segs than the sum of the remaining part segs
                        #So distribute the extra count
                        distributeCnt(maxSegCntsByPart, j, (partSegCnt - remainingSegs))
                        
                        #Also, adjust the seg count of the last part of the previous 
                        #segments that had fewer than max number of parts
                        for k in range(0, i):
                            if(len(sortedElems[k].parts) < len(maxSegCntsByPart)):
                                totalSegs = sum(maxSegCntsByPart)
                                existingSegs = sum(maxSegCntsByPart[:len(sortedElems[k].parts)-1])
                                resSegCnt[k][-1] = totalSegs - existingSegs
                    
                elif(partSegCnt > maxSegCntsByPart[j]):
                    maxSegCntsByPart[j] = partSegCnt
    for i, path in enumerate(sortedPaths):

        if(byPart == False):
            partView = path.getPartView()
            segCnt = partView.getSegCnt()
            diff = maxSegCnt - segCnt

            if(diff > 0):
                cnts = getSubdivCntPerSeg(partView, diff)
                cumulSegIdx = 0
                for j in range(0, len(path.parts)):
                    part = path.parts[j]
                    newSegs = []
                    for k, seg in enumerate(part.getSegs()):
                        numSubdivs = cnts[cumulSegIdx] + 1
                        newSegs += subdivideSeg(seg, numSubdivs)
                        cumulSegIdx += 1
                    
                    path.parts[j] = Part(path, newSegs, part.isClosed)
        else:
            for j in range(0, len(path.parts)):
                part = path.parts[j]
                newSegs = []

                partSegCnt = part.getSegCnt()

                #TODO: Adding everything in the last part?
                if(j == (len(path.parts)-1) and 
                    len(maxSegCntsByPart) > len(path.parts)):
                    diff = resSegCnt[i][j] - partSegCnt
                else:    
                    diff = maxSegCntsByPart[j] - partSegCnt
                    
                if(diff > 0):
                    cnts = getSubdivCntPerSeg(part, diff)

                    for k, seg in enumerate(part.getSegs()):
                        seg = part.getSeg(k)
                        subdivCnt = cnts[k] + 1 #1 for the existing one
                        newSegs += subdivideSeg(seg, subdivCnt)
                    
                    #isClosed won't be used, but let's update anyway
                    path.parts[j] = Part(path, newSegs, part.isClosed)

def alignPath(path, matchParts, matchCriteria, alignBy, alignValues):

    parts = path.parts[:]    

    if(matchParts):
        fnMap = {'vCnt' : lambda part: -1 * part.getSegCnt(), \
                 'bbArea': lambda part: -1 * part.bboxSurfaceArea(worldSpace = True), \
                 'bbHeight' : lambda part: -1 * part.getBBHeight(worldSpace = True), \
                 'bbWidth' : lambda part: -1 * part.getBBWidth(worldSpace = True), \
                 'bbDepth' : lambda part: -1 * part.getBBDepth(worldSpace = True)
                }
        matchPartCmpFns = []
        for criterion in matchCriteria:
            fn = fnMap.get(criterion)
            if(fn == None):
                minmax = criterion[:3] == 'max' #0 if min; 1 if max
                axisIdx = ord(criterion[3:]) - ord('X')
                
                fn = eval('lambda part: part.getBBox(worldSpace = True)[' + \
                    str(minmax) + '][' + str(axisIdx) + ']')
                    
            matchPartCmpFns.append(fn)
        
        def comparer(left, right):
            for fn in matchPartCmpFns:
                a = fn(left)
                b = fn(right)
                
                if(floatCmpWithMargin(a, b)):
                    continue
                else:
                    return (a > b) - ( a < b) #No cmp in python3

            return 0
            
        parts = sorted(parts, key = cmp_to_key(comparer))
        
    alignCmpFn = None
    if(alignBy == 'vertCo'):            
        def evalCmp(criteria, pt1, pt2):
            if(len(criteria) == 0):
                return True
                
            minmax = criteria[0][0]
            axisIdx = criteria[0][1]
            val1 = pt1[axisIdx]
            val2 = pt2[axisIdx]
            
            if(floatCmpWithMargin(val1, val2)):
                criteria = criteria[:]
                criteria.pop(0)
                return evalCmp(criteria, pt1, pt2)
            
            return val1 < val2 if minmax == 'min' else val1 > val2

        alignCri = [[a[:3], ord(a[3:]) - ord('X')] for a in alignValues]
        alignCmpFn = lambda pt1, pt2, curve: (evalCmp(alignCri, \
            curve.matrix_world @ pt1, curve.matrix_world @ pt2))

    startPt = None
    startIdx = None
    
    for i in range(0, len(parts)):        
        #Only truly closed parts
        if(alignCmpFn != None and parts[i].isClosed):
            for j in range(0, parts[i].getSegCnt()):
                seg = parts[i].getSeg(j)
                if(j == 0 or alignCmpFn(seg.start, startPt, path.curve)):
                    startPt = seg.start
                    startIdx = j
                    
            path.parts[i]= Part(path, parts[i].getSegsCopy(startIdx, None) + \
                parts[i].getSegsCopy(None, startIdx), parts[i].isClosed)
        else:
            path.parts[i] = parts[i]
            
#TODO: Other shape key attributes like interpolation...
def getExistingShapeKeyPaths(path):
    obj = path.curve
    paths = []
    
    if(obj.data.shape_keys != None):
        keyblocks = obj.data.shape_keys.key_blocks[1:]#Skip basis
        for key in keyblocks:
            datacopy = obj.data.copy()
            i = 0
            for spline in datacopy.splines:
                for pt in spline.bezier_points:
                    pt.co = key.data[i].co
                    pt.handle_left = key.data[i].handle_left
                    pt.handle_right = key.data[i].handle_right
                    i += 1 
            paths.append(Path(obj, datacopy, key.name))
    return paths
    
def addShapeKey(curve, paths, space):
    for path in paths:
        key = curve.shape_key_add(name = path.name)
        pts = [pt for pset in getSplineDataForPath(path) for pt in pset]
        for i, pt in enumerate(pts):
            if(space == 'worldspace'):
                pt = [curve.matrix_world.inverted() @ (path.curve.matrix_world @ p) for p in pt]
            key.data[i].co = pt[0]
            key.data[i].handle_left = pt[1]
            key.data[i].handle_right = pt[2]
            
def safeRemoveCurveObj(obj):
    #TODO: Check situations where the obj is already removed
    try:
        collections = obj.users_collection

        for c in collections:
            c.objects.unlink(obj)
            
        if(obj.name in bpy.context.scene.collection.objects):
            bpy.context.scene.collection.objects.unlink(obj)
            
        if(obj.data.users == 1):
            bpy.data.curves.remove(obj.data) #This also removes object?        
        else:
            bpy.data.objects.remove(obj)
    except:
        pass

def addCurve(path):
    splineData = getSplineDataForPath(path)
    curveData = getNewCurveData(bpy, splineData, path)
    obj = path.curve.copy()
    obj.data = curveData
    if(obj.data.shape_keys != None):
        keyblocks = reversed(obj.data.shape_keys.key_blocks)
        for sk in keyblocks:
            obj.shape_key_remove(sk)
    
    collections = path.curve.users_collection
    for collection in collections:
        collection.objects.link(obj)

    if(path.curve.name in bpy.context.scene.collection.objects and \
        obj.name not in bpy.context.scene.collection.objects):
        bpy.context.scene.collection.objects.link(obj)

    return obj

def getNewCurveData(bpy, splinesData, path):

    newCurveData = path.curve.data.copy()
    newCurveData.splines.clear()

    for i, pointSets in enumerate(splinesData):
        spline = newCurveData.splines.new('BEZIER')
        spline.bezier_points.add(len(pointSets)-1)
        spline.use_cyclic_u = path.parts[i].toClose
        
        for j in range(0, len(spline.bezier_points)):
            pointSet = pointSets[j]
            spline.bezier_points[j].co = pointSet[0]
            spline.bezier_points[j].handle_left = pointSet[1]
            spline.bezier_points[j].handle_right = pointSet[2]
            spline.bezier_points[j].handle_right_type = 'FREE'

    return newCurveData
    
def getSplineDataForPath(path):
    splinesData = []
    
    for i, part in enumerate(path.parts):
        prevSeg = None
        pointSets = []

        for j, seg in enumerate(part.getSegs()):
            
            pt = seg.start
            handleRight = seg.ctrl1
            
            if(j == 0):
                if(path.parts[i].toClose):
                    handleLeft = part.getSeg(-1).ctrl2
                else:
                    handleLeft = pt
            else:
                handleLeft = prevSeg.ctrl2
                
            pointSets.append([pt, handleLeft, handleRight])
            prevSeg = seg
    
        if(path.parts[i].toClose == True):
            pointSets[-1][2] = seg.ctrl1
        else:
            pointSets.append([prevSeg.end, prevSeg.ctrl2, prevSeg.end])
            
        splinesData.append(pointSets)
        
    return splinesData

