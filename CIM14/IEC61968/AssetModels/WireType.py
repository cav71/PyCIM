# Copyright (C) 2010 Richard Lincoln
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA, USA

from CIM14.IEC61970.Core.IdentifiedObject import IdentifiedObject

class WireType(IdentifiedObject):
    """Wire conductor (per IEEE specs). A specific type of wire or combination of wires, not insulated from each other, suitable for carrying electrical current.
    """

    def __init__(self, material="acsr", rAC25=0.0, sizeDescription='', rAC75=0.0, radius=0.0, coreRadius=0.0, rAC50=0.0, gmr=0.0, rDC20=0.0, ratedCurrent=0.0, coreStrandCount=0, strandCount=0, WireArrangements=None, ConcentricNeutralCableInfos=None, *args, **kw_args):
        """Initialises a new 'WireType' instance.

        @param material: Wire material. Values are: "acsr", "steel", "aluminum", "copper", "other"
        @param rAC25: AC resistance per unit length of the conductor at 25 degrees C. 
        @param sizeDescription: Describes the wire guage or cross section (e.g., 4/0, #2, 336.5). 
        @param rAC75: AC resistance per unit length of the conductor at 75 degrees C. 
        @param radius: Outside radius of the wire. 
        @param coreRadius: (if there is a different core material) Radius of the central core. 
        @param rAC50: AC resistance per unit length of the conductor at 50 degrees C. 
        @param gmr: Geometric Mean Radius. If we replace the conductor by a thin walled tube of radius GMR, then its reactance is identical to the reactance of the actual conductor. 
        @param rDC20: DC resistance per unit length of the conductor at 20 degrees C. 
        @param ratedCurrent: Current carrying capacity of the wire under stated thermal conditions. 
        @param coreStrandCount: (if used) Number of strands in the steel core. 
        @param strandCount: Number of strands in the wire. 
        @param WireArrangements: All wire arrangements using this wire type.
        @param ConcentricNeutralCableInfos: All concentric neutral cables using this wire type.
        """
        #: Wire material. Values are: "acsr", "steel", "aluminum", "copper", "other"
        self.material = material

        #: AC resistance per unit length of the conductor at 25 degrees C.
        self.rAC25 = rAC25

        #: Describes the wire guage or cross section (e.g., 4/0, #2, 336.5).
        self.sizeDescription = sizeDescription

        #: AC resistance per unit length of the conductor at 75 degrees C.
        self.rAC75 = rAC75

        #: Outside radius of the wire.
        self.radius = radius

        #: (if there is a different core material) Radius of the central core.
        self.coreRadius = coreRadius

        #: AC resistance per unit length of the conductor at 50 degrees C.
        self.rAC50 = rAC50

        #: Geometric Mean Radius. If we replace the conductor by a thin walled tube of radius GMR, then its reactance is identical to the reactance of the actual conductor.
        self.gmr = gmr

        #: DC resistance per unit length of the conductor at 20 degrees C.
        self.rDC20 = rDC20

        #: Current carrying capacity of the wire under stated thermal conditions.
        self.ratedCurrent = ratedCurrent

        #: (if used) Number of strands in the steel core.
        self.coreStrandCount = coreStrandCount

        #: Number of strands in the wire.
        self.strandCount = strandCount

        self._WireArrangements = []
        self.WireArrangements = [] if WireArrangements is None else WireArrangements

        self._ConcentricNeutralCableInfos = []
        self.ConcentricNeutralCableInfos = [] if ConcentricNeutralCableInfos is None else ConcentricNeutralCableInfos

        super(WireType, self).__init__(*args, **kw_args)

    _attrs = ["material", "rAC25", "sizeDescription", "rAC75", "radius", "coreRadius", "rAC50", "gmr", "rDC20", "ratedCurrent", "coreStrandCount", "strandCount"]
    _attr_types = {"material": str, "rAC25": float, "sizeDescription": str, "rAC75": float, "radius": float, "coreRadius": float, "rAC50": float, "gmr": float, "rDC20": float, "ratedCurrent": float, "coreStrandCount": int, "strandCount": int}
    _defaults = {"material": "acsr", "rAC25": 0.0, "sizeDescription": '', "rAC75": 0.0, "radius": 0.0, "coreRadius": 0.0, "rAC50": 0.0, "gmr": 0.0, "rDC20": 0.0, "ratedCurrent": 0.0, "coreStrandCount": 0, "strandCount": 0}
    _enums = {"material": "ConductorMaterialKind"}
    _refs = ["WireArrangements", "ConcentricNeutralCableInfos"]
    _many_refs = ["WireArrangements", "ConcentricNeutralCableInfos"]

    def getWireArrangements(self):
        """All wire arrangements using this wire type.
        """
        return self._WireArrangements

    def setWireArrangements(self, value):
        for x in self._WireArrangements:
            x.WireType = None
        for y in value:
            y._WireType = self
        self._WireArrangements = value

    WireArrangements = property(getWireArrangements, setWireArrangements)

    def addWireArrangements(self, *WireArrangements):
        for obj in WireArrangements:
            obj.WireType = self

    def removeWireArrangements(self, *WireArrangements):
        for obj in WireArrangements:
            obj.WireType = None

    def getConcentricNeutralCableInfos(self):
        """All concentric neutral cables using this wire type.
        """
        return self._ConcentricNeutralCableInfos

    def setConcentricNeutralCableInfos(self, value):
        for x in self._ConcentricNeutralCableInfos:
            x.WireType = None
        for y in value:
            y._WireType = self
        self._ConcentricNeutralCableInfos = value

    ConcentricNeutralCableInfos = property(getConcentricNeutralCableInfos, setConcentricNeutralCableInfos)

    def addConcentricNeutralCableInfos(self, *ConcentricNeutralCableInfos):
        for obj in ConcentricNeutralCableInfos:
            obj.WireType = self

    def removeConcentricNeutralCableInfos(self, *ConcentricNeutralCableInfos):
        for obj in ConcentricNeutralCableInfos:
            obj.WireType = None

