from .matrixgroup import *
from .imagingpath import *


class LaserPath(MatrixGroup):
    """The main class of the module for coherent
    laser beams: it is the combination of Matrix() or MatrixGroup()
    to be used as a laser path with a laser beam (GaussianBeam)
    at the entrance.

    Usage is to create the LaserPath(), then append() elements
    and display(). You may change the inputBeam to any GaussianBeam(),
    or provide one to display(beam=GaussianBeam())

    Parameters
    ----------
    elements : list of elements
        A list of ABCD matrices in the imaging path
    label : string
        the label for the imaging path (Optional)

    Attributes
    ----------
    inputBeam : object of GaussianBeam class
        the input beam of the imaging path is defined using this parameter.
    showElementLabels : bool
        If True, the labels of the elements will be shown on display. (default=True)
    showPointsOfInterest : bool
        If True, the points of interest will be shown on display. (default=True)
    showPointsOfInterestLabels : bool
        If True, the labels of the points of interest will be shown on display. (default=True)
    showPlanesAcrossPointsOfInterest : bool
        If True, the planes across the points of interest will be shown on display. (default=True)

    See Also
    --------
    raytracing.GaussianBeam

    Notes
    -----
    Gaussian laser beams are not "blocked" by aperture. The formalism
    does not explicitly allow that.  However, if it appears that a 
    GaussianBeam() would be clipped by  finite aperture, a property 
    is set to indicate it, but it will propagate nevertheless
    and without diffraction due to that aperture.
    """

    def __init__(self, elements=None, label=""):
        self.inputBeam = None
        self.showElementLabels = True
        self.showPointsOfInterest = True
        self.showPointsOfInterestLabels = True
        self.showPlanesAcrossPointsOfInterest = True
        super(LaserPath, self).__init__(elements=elements, label=label)

    def display(self, inputBeams=None, comments=None):  # pragma: no cover
        """ Display the optical system and trace the laser beam. 
        If comments are included they will be displayed on a
        graph in the bottom half of the plot.

        Parameters
        ----------
        inputBeams : list of object of GaussianBeam class
            A list of Gaussian beams
        comments : string
            If comments are included they will be displayed on a graph in the bottom half of the plot. (default=None)

        """

        if inputBeams is not None:
            beams = inputBeams
        else:
            beams = [self.inputBeam]

        if self.label == "":
            self.label = "User-specified gaussian beams"

        if comments is not None:
            fig, (axes, axesComments) = plt.subplots(2, 1, figsize=(10, 7))
            axesComments.axis('off')
            axesComments.text(0., 1.0, comments, transform=axesComments.transAxes,
                              fontsize=10, verticalalignment='top')
        else:
            fig, axes = plt.subplots(figsize=(10, 7))

        self.createBeamTracePlot(axes=axes, beams=beams)

        self._showPlot()

    def createBeamTracePlot(self, axes, beams):  # pragma: no cover
        """ Create a matplotlib plot to draw the laser beam and the elements.
        """

        displayRange = 2 * self.largestDiameter
        if displayRange == float('+Inf'):
            displayRange = self.inputBeam.w * 6

        axes.set(xlabel='Distance', ylabel='Height', title=self.label)
        axes.set_ylim([-displayRange / 2 * 1.2, displayRange / 2 * 1.2])

        self.drawAt(z=0, axes=axes)

        for beam in beams:
            self.drawBeamTrace(axes, beam)
            self.drawWaists(axes, beam)

        return axes

    def rearrangeBeamTraceForPlotting(self, rayList):
        x = []
        y = []
        for ray in rayList:
            x.append(ray.z)
            y.append(ray.w)
        return (x, y)

    def drawBeamTrace(self, axes, beam):  # pragma: no cover
        """ Draw beam trace corresponding to input beam 
        Because the laser beam diffracts through space, we cannot
        simply propagate the beam over large distances and trace it
        (as opposed to rays, where we can). We must split Space() 
        elements into sub elements to watch the beam size expand.
        
        We arbitrarily split Space() elements into N sub elements
        before plotting.
        """

        N = 100
        highResolution = ImagingPath()
        for element in self.elements:
            if isinstance(element, Space):
                for i in range(N):
                    highResolution.append(Space(d=element.L / N,
                                                n=element.frontIndex))
            else:
                highResolution.append(element)

        beamTrace = highResolution.trace(beam)
        (x, y) = self.rearrangeBeamTraceForPlotting(beamTrace)
        axes.plot(x, y, 'r', linewidth=1)
        axes.plot(x, [-v for v in y], 'r', linewidth=1)

    def drawWaists(self, axes, beam):  # pragma: no cover
        """ Draws the expected waist (i.e. the focal spot or the spot where the
        size is minimum) for all positions of the beam. This will show "waists" that
        are virtual if there is an additional lens between the beam and the expceted
        waist.

        It is easy to obtain the waist position from the complex radius of curvature
        because it is the position where the complex radius is imaginary. The position
        returned is relative to the position of the beam, which is why we add the actual
        position of the beam to the relative position. """

        (xScaling, yScaling) = self.axesToDataScale(axes)
        arrowWidth = xScaling * 0.01
        arrowHeight = yScaling * 0.03
        arrowSize = arrowHeight * 3

        beamTrace = self.trace(beam)
        for beam in beamTrace:
            relativePosition = beam.waistPosition
            position = beam.z + relativePosition
            size = beam.waist

            axes.arrow(position, size + arrowSize, 0, -arrowSize,
                       width=0.1, fc='g', ec='g',
                       head_length=arrowHeight, head_width=arrowWidth,
                       length_includes_head=True)
            axes.arrow(position, -size - arrowSize, 0, arrowSize,
                       width=0.1, fc='g', ec='g',
                       head_length=arrowHeight, head_width=arrowWidth,
                       length_includes_head=True)

