#!/usr/bin/python -B
"""
Creates a random population.
Evolves the population, selecting according to aestetics.
Saves the entire population at each generation.
"""
import sys
import datetime

import cell
import evolve



# =============================================================================
# FITNESS FUNCTION
#
# This is the most important piece
#
def fit_surface(code):

    # create the body to be evaluated
    body = cell.Body(code)

    # estimate body extension
    # --> select for spread bodies
    #
    x = [c.cx for c in body]
    y = [c.cy for c in body]
    w = max(x) - min(x)
    h = max(y) - min(y)
    body_extension = w * h
    if body_extension == 0: return -1

    # calculate variance of cell sizes
    # --> select for similar cell sizes
    #
    sizes = [ c.width*c.height for c in body ]
    x = sum(sizes)
    xx = sum( s*s for s in sizes )

    cells_variance = 1 + xx - x*x/len(sizes)
    cells_surface = x

    # calculate distance from optimal ratio
    # --> select for optimal surface to extension ratio
    ratio = cells_surface / body_extension
    ideal_ratio = .5**2
    f = (ratio-ideal_ratio)**2

    # --> select for many cells
    # --> select against long genetic code
    return  ( len(body)/30 - len(code)/1000 ) / f / cells_variance





# =============================================================================
# MAIN
#
def main():

    # evolution
    ev = evolve.evolution(fit_surface, cell.Cell.code_symbols, ' ')

    # output file
    fn = 'genesis'+datetime.datetime.now().strftime('%y%m%d_%H%M%S')
    if len(sys.argv) > 1: fn = sys.argv[1]
    out = open(fn, 'wt')

    # evolve
    while ev.generation < 2000:
        fitness, best_code = ev.iterate()

        # output
        body = cell.Body(best_code)
        print 'generation:%3d  genome length:%d  cells:%d' % (ev.generation, len(best_code), len(body))

        # save and flush
        out.write('#####        generation %d\n' % ev.generation)
        out.write('\n'.join(ev.pop))
        out.write('\n')
        out.flush()



if __name__ == '__main__':
    main()



#EOF ==========================================================================
