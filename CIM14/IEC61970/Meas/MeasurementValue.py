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

class MeasurementValue(IdentifiedObject):
    """The current state for a measurement. A state value is an instance of a measurement from a specific source. Measurements can be associated with many state values, each representing a different source for the measurement.
    """

    def __init__(self, sensorAccuracy=0.0, timeStamp='', MeasurementValueSource=None, RemoteSource=None, MeasurementValueQuality=None, *args, **kw_args):
        """Initialises a new 'MeasurementValue' instance.

        @param sensorAccuracy: The limit, expressed as a percentage of the sensor maximum, that errors will not exceed when the sensor is used under  reference conditions. 
        @param timeStamp: The time when the value was last updated 
        @param MeasurementValueSource: A reference to the type of source that updates the MeasurementValue, e.g. SCADA, CCLink, manual, etc. User conventions for the names of sources are contained in the introduction to IEC 61970-301.
        @param RemoteSource: Link to the physical telemetered point associated with this measurement.
        @param MeasurementValueQuality: A MeasurementValue has a MeasurementValueQuality associated with it.
        """
        #: The limit, expressed as a percentage of the sensor maximum, that errors will not exceed when the sensor is used under  reference conditions.
        self.sensorAccuracy = sensorAccuracy

        #: The time when the value was last updated
        self.timeStamp = timeStamp

        self._MeasurementValueSource = None
        self.MeasurementValueSource = MeasurementValueSource

        self._RemoteSource = None
        self.RemoteSource = RemoteSource

        self._MeasurementValueQuality = None
        self.MeasurementValueQuality = MeasurementValueQuality

        super(MeasurementValue, self).__init__(*args, **kw_args)

    _attrs = ["sensorAccuracy", "timeStamp"]
    _attr_types = {"sensorAccuracy": float, "timeStamp": str}
    _defaults = {"sensorAccuracy": 0.0, "timeStamp": ''}
    _enums = {}
    _refs = ["MeasurementValueSource", "RemoteSource", "MeasurementValueQuality"]
    _many_refs = []

    def getMeasurementValueSource(self):
        """A reference to the type of source that updates the MeasurementValue, e.g. SCADA, CCLink, manual, etc. User conventions for the names of sources are contained in the introduction to IEC 61970-301.
        """
        return self._MeasurementValueSource

    def setMeasurementValueSource(self, value):
        if self._MeasurementValueSource is not None:
            filtered = [x for x in self.MeasurementValueSource.MeasurementValues if x != self]
            self._MeasurementValueSource._MeasurementValues = filtered

        self._MeasurementValueSource = value
        if self._MeasurementValueSource is not None:
            if self not in self._MeasurementValueSource._MeasurementValues:
                self._MeasurementValueSource._MeasurementValues.append(self)

    MeasurementValueSource = property(getMeasurementValueSource, setMeasurementValueSource)

    def getRemoteSource(self):
        """Link to the physical telemetered point associated with this measurement.
        """
        return self._RemoteSource

    def setRemoteSource(self, value):
        if self._RemoteSource is not None:
            self._RemoteSource._MeasurementValue = None

        self._RemoteSource = value
        if self._RemoteSource is not None:
            self._RemoteSource.MeasurementValue = None
            self._RemoteSource._MeasurementValue = self

    RemoteSource = property(getRemoteSource, setRemoteSource)

    def getMeasurementValueQuality(self):
        """A MeasurementValue has a MeasurementValueQuality associated with it.
        """
        return self._MeasurementValueQuality

    def setMeasurementValueQuality(self, value):
        if self._MeasurementValueQuality is not None:
            self._MeasurementValueQuality._MeasurementValue = None

        self._MeasurementValueQuality = value
        if self._MeasurementValueQuality is not None:
            self._MeasurementValueQuality.MeasurementValue = None
            self._MeasurementValueQuality._MeasurementValue = self

    MeasurementValueQuality = property(getMeasurementValueQuality, setMeasurementValueQuality)

