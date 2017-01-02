"""
Classes for morphogenesis of cells and body.
by Francesco Orsenigo


This module can translate an arbitrary string of symbols into
an abstract shape that mocks simple life forms.

As the information on the string remains coherent regardless of
the operations performed on it, it is an optimal target for
a genetic algorithm.

Each symbol is represented by an ASCII char and 'cell.code_symbol'
contains all the significant symbols.

The draw() functions render the cells as GL rectangles.

"""



import math
import itertools
from pyglet.gl import *



# OpenGL deals in degrees, and so do we

def deg_sin(angle):
    return math.sin( angle*math.pi/180 )

def deg_cos(angle):
    return math.cos( angle*math.pi/180 )





class Cell:
    """
    The basic building block of a body.

    """

    # these constants regulate how much a symbol expression translates
    # into a cell's features
    turn_factor = 5
    width_factor = 1.1
    height_factor = 1.1
    gem_threshold = 7
    generation_factor = .5



    # This defines where on a cell children can gem.
    stem_coordinates = {
        # width coefficient, height coefficient, angle
        '<': [ +.5, .0, -90],  # left
        '^': [  .0, .5,   0],  # top
        '>': [ +.5, .0, +90],  # right
    }


    # Each different stem promoter symbol will redirect all subsequent
    # code expressions towards the corresponding stem.
    stem_symbols = stem_coordinates.keys()


    # The relative strength of morphogens determine which target sequence
    # will be activated for the development of a cell.
    # The 'generation' morphogen depends on a cell's generation, while
    # 'code' morphogens are expressed by genetic code
    generation_morphogen = 'gen'
    code_morphogens = ['n', 's', 'e', 'w']
    morphogens = code_morphogens + [generation_morphogen]

    code_promoters = {
        'stop':  ' ',
        'left':  'l',
        'right': 'r',
        'widen': '-',
        'rise':  '|',
    }



    # List of all the valid symbols that can appear in a genetic code.
    code_symbols = sorted(code_morphogens + stem_symbols + code_promoters.values())



    # According to the hierarchy of their concentrations, morphogens
    # will activate different target sequences of the DNA:
    # each possible morphogen hierarchy permutation indicates an arbitrary
    # target sequence from which to start transcription.
    #
    # There should be roughly as many unique target sequences
    # as hierarchy permutations.
    #
    # With about 10 different base symbols, there are about 100
    # couples of bases from which to choose from.
    # This also means that a rna of about 1000 bases will contain
    # many of these bases several times.

    # translation dictionary from morphogen hierarchies to target sequences
    target_sequences = dict([
        (''.join(hierarchy), ''.join(target_sequence)) for hierarchy, target_sequence in
        zip(
            itertools.permutations(morphogens),
            itertools.cycle(itertools.product(code_symbols, repeat=2))
        )])




    # this instead is used for drawing
    square = ((-.5, -.5), (+.5, -.5), (+.5, +.5), (-.5, +.5))





    def __init__(self, body, target_sequence, parent=None):
        """ """
        body.append(self)
        self.body = body
        self.type = target_sequence
        self.generation = parent.generation+1 if parent else 0

        # body structure
        self.parent = parent
        self.children = dict((stem, None) for stem in self.stem_symbols)

        # stress values, used to animate
        self.stress_angle = .0
        self.stress_ratio = 1.       # multiplies width, divides height
        self.stress_angle_time = .0
        self.stress_ratio_time = .0

        # morphogenesis steps
        self.express_genome(target_sequence)
        self.express_to_traits()
        self.express_to_stems()

        # the normalized expression values are used to determine aesthetic properties
        n = float(max(self.expression.values()))
        for k in self.expression:
            self.expression[k] /= n if n else 1



    def express_genome(self, target_sequence):
        """
        Express all occourrences of target_sequence in the genome.

        """
        self.expression = dict( (b, 0) for b in self.code_symbols )


        ##@@ this dictionary generation seems to be especially slow, should be cached
        #self.stem_expression_cached.deepcopy()
        self.stem_expression = dict( [s, dict([m, 0] for m in self.code_morphogens)] for s in self.stem_symbols)

        # Find targets and express all bases sequentially,
        # stopping when you find the stop marker.
        for s in self.body.genome.split(target_sequence)[1:]:
            target_stem = '^'
            for b in s:
                # change the stem to which apply all subsequent morphogens
                if b in self.stem_symbols:
                    target_stem = b
                # apply morphogens only to targeted stem
                if b in self.code_morphogens:
                    self.stem_expression[target_stem][b] += 1
                # count symbols occourrences
                self.expression[b] += 1
                # stop symbol will interrupt transcription
                if b == ' ': break



    def express_to_traits(self):
        """
        Sets cell traits according to symbol expression.

        """
        ex = self.expression

        # turn
        self.relax_angle = (ex['r'] - ex['l']) * self.turn_factor

        # resize
        self.relax_width = self.width_factor ** ex['-']
        self.relax_height = self.height_factor ** ex['|']



    def express_to_stems(self):
        """ """
        for s in self.stem_symbols:
            strengths = self.stem_expression[s]
            if sum(strengths.values()) > self.gem_threshold * 1.02**self.generation:

                # add generation morphogen
                # it is added only now not to interfere with the gem_threshold calculation
                strengths[self.generation_morphogen] = self.generation * self.generation_factor

                # find hierarchy of morphogens strengths
                h = ''.join(sorted(strengths, key=strengths.get))

                # translate hierarchy into a target sequence
                target_sequence = self.target_sequences[h]

                # mark the stem for spawning
                self.children[s] = target_sequence



    def gem(self):
        """
        Create a new cell at a stem point.

        """
        cnt = 0
        for stem in self.stem_symbols:
            target_sequence = self.children[stem]
            if type(target_sequence) is str:
                self.children[stem] = Cell(self.body, target_sequence, self)
                cnt += 1
        return cnt





    def recursive_set_coordinates(self, x=.0, y=.0, stem_angle=.0):
        """ """
        # update width and height
        self.width = self.relax_width * self.stress_ratio
        self.height = self.relax_height / self.stress_ratio

        # resulting angle depends on all previous angles
        self.angle = math.fmod(stem_angle + self.relax_angle + self.stress_angle, 360)

        # the cell is attached by its bottom side
        # thus the center is displaced by the cell's height
        self.cx = x + deg_sin(self.angle) * self.height/2
        self.cy = y + deg_cos(self.angle) * self.height/2


        # update children
        for s in self.stem_symbols:
            child = self.children[s]
            if child:
                wf, hf, a = self.stem_coordinates[s]

                # calculate stem angle
                sa = self.angle + a

                # calculate stem position
                l = wf*self.width + hf*self.height
                sx = self.cx + l*deg_sin(sa)
                sy = self.cy + l*deg_cos(sa)

                # update child
                child.recursive_set_coordinates(sx, sy, sa)



    def animate(self):
        """ """
        if not self.parent:
            return

        # stress angle
        self.stress_angle_time = (self.stress_angle_time + 10*self.expression['s']) % 360
        self.stress_angle = deg_sin(self.stress_angle_time) * 10*self.expression['n']

        # stress ratio
        self.stress_ratio_time = (self.stress_ratio_time + 10*self.expression['e']) % 360
        self.stress_ratio = 1.3 ** deg_sin(self.stress_ratio_time)





    def draw(self):
        """ """
        # isolate matrix operations
        glPushMatrix()

        glTranslated(self.cx, self.cy, 0)
        glRotated(self.angle, 0, 0, -1)
        glScaled(self.width, self.height, 1)

        # solid cell body
        e = self.expression
        glColor4f(e[' ']/3, e['|']/2, .5+e['^']/2, .8)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        glBegin(GL_QUADS)
        for v in self.square:
            glVertex2f(*v)
        glEnd()

        # contour
        glBegin(GL_LINE_LOOP)
        glColor4f(0, 0, 1, .9)
        for v in self.square:
            glVertex2f(*v)
        glEnd()

        glPopMatrix()







class Body(list):
    """
    A clump of cells sharing the same genetic material.

    """

    # if a generation passes this limit, no new cells are created.
    cells_limit = 50



    def __init__(self, genome):
        """ """
        self.genome = genome

        # start body with strongest target sequence
        best = max( (genome.count(s), s) for s in Cell.target_sequences.values() )[1]

        # generate body
        self.root = Cell(self, best)
        new_cells = 1
        last_generation = self.root.generation
        while new_cells > 0 and len(self) < self.cells_limit:
            new_cells = 0
            for cell in self:
                if cell.generation == last_generation:
                    new_cells += cell.gem()
            last_generation += 1

        # clean up
        for cell in self:
            for s in cell.children:
                if not isinstance(cell.children[s], Cell):
                    cell.children[s] = None

        # shape body
        self.scale = None
        self.update_coordinates()



    # recalculates cell tree geometry
    def update_coordinates(self):
        """ """
        self.root.recursive_set_coordinates()






    def update(self):
        """
        Executes a whole time iteration.

        """
        for c in self:
            c.animate()

        self.update_coordinates()



    def draw(self):
        """ """
        x = [c.cx for c in self]
        y = [c.cy for c in self]
        ox = (max(x)+min(x)) /2
        oy = (max(y)+min(y)) /2

        if not self.scale:
            w = max(x)-min(x)
            h = max(y)-min(y)
            self.scale = 2./max(w, h, self.root.width)

        glPushMatrix()
        glScaled(self.scale, self.scale, 1)
        glTranslated(-ox, -oy, 0)
        for c in self:
            c.draw()
        glPopMatrix()




if __name__ == '__main__':
    print 'morphogens: ', Cell.morphogens
    print 'promoters:', Cell.code_promoters.values()
    print 'stems:', Cell.stem_symbols

#EOF
