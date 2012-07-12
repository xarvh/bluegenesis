#!/usr/bin/python -B
"""
Loads and display populations through their whole evolutionary history.

"""
from pyglet.gl import *
import pyglet.window.key as key
import random
import sys

import cell





class Gui:

    def __init__(self, pops):

        # list of populations
        self.pops = pops

        # selected generation
        self.sgen = 0

        # selected individual
        self.sind = 0

        # displayed body
        self.dbody = cell.Body(self.pops[0][0])

        # actual GUI
        self.window = pyglet.window.Window()
        self.keys = key.KeyStateHandler()
        self.window.push_handlers(self.keys)
        self.window.on_draw = self.draw
        def update(latency):
            self.keyboard_input()
            self.dbody.update()
        pyglet.clock.schedule_interval(update, 0.1)



    def keyboard_input(self):
        if self.keys[key.LEFT]: self.select_individual(-1)
        if self.keys[key.RIGHT]: self.select_individual(+1)
        if self.keys[key.UP]: self.select_generation(-1)
        if self.keys[key.DOWN]: self.select_generation(+1)
#        if symbol == key.s: screenshot.take()
#        if symbol == key.ENTER:
#            print 'saving genome'
#            open('new_genomes', 'ab').write(sw.body.genome + '\n')



    def reset_body(self):
        self.dbody = cell.Body(self.pops[self.sgen][self.sind])


    def select_individual(self, step):
        self.sind += step
        self.sind %= len(self.pops[self.sgen])
        self.reset_body()


    def select_generation(self, step):
        self.sgen += step
        self.sgen %= len(self.pops)
        self.reset_body()



    def draw(self):

        self.window.clear()

        # glMatrixMode interferes with text rendering
        glPushMatrix()
        #glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        w = self.window.width
        h = self.window.height
        glTranslated(w/2, h/2, 0)
        glScaled(h/2, h/2, 1)   # want uniform coordinates
        #glMatrixMode(GL_MODELVIEW)

        glPushMatrix()
        glScaled(.6, .6, 1)
        self.dbody.draw()
        glPopMatrix()
        glPopMatrix()


        # write label
        text = "ind %d/%d, gen %d/%d, cells %d" % (
            self.sind, len(self.pops[self.sgen]),
            self.sgen, len(self.pops),
            len(self.dbody)
        )
        glPushMatrix()
        pyglet.text.Label(text,
            font_name='Times New Roman', font_size=20,
            x=5, y=5, anchor_x='left', anchor_y='bottom').draw()
        glPopMatrix()





    # perform operations that required drawing to be completed
    def after_draw(self):
        pass









#=========================================================================================


"""
class screenshot:
    cnt = 0
    @staticmethod
    def take(name=None):
        if not name:
            screenshot.cnt += 1
            name = 'shot%04d.png' % screenshot.cnt
        pyglet.image.get_buffer_manager().get_color_buffer().save(name)





    def after_draw(self):
        if '--shot' in sys.argv:
            screenshot.take('movie%04d.png' % self.total_cnt)

        self.total_cnt += 1

        if not self.free:
            self.frames_cnt += 1
            if self.frames_cnt >= self.frames_per_body:
                if self.genomes:
                    self.next()
                else:
                    sys.exit(0)
"""



# =============================================================================

def get_random_code():
    return ''.join([ random.choice(cell.Cell.code_symbols) for i in xrange(1000)])



def main():

    if len(sys.argv) > 1:
        gui = Gui([gen.split('\n')[1:] for gen in open(sys.argv[1]).read().split('###')[1:]])
    else:
        gui = Gui([[get_random_code() for i in xrange(50)]])

    pyglet.app.run()


if __name__ == '__main__':
    main()

#EOF ==========================================================================
