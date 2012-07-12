#!/usr/bin/python -B
"""
Carries the evolution iteration of a population, according to the given
fitness function.

"""
import random





class evolution:
    """ """

    @staticmethod
    def create_initial_pop(code_symbols, code_length=2, pop_size=100):
        """ """
        return [
            ''.join(random.choice(code_symbols) for i in xrange(code_length))
            for p in xrange(pop_size)]



    def __init__(self, fitness_function, code_symbols, break_symbol, initial_pop=None):
        """ """
        self.code_symbols = code_symbols
        self.break_symbol = break_symbol
        self.fitness_function = fitness_function
        self.pop = initial_pop or self.create_initial_pop(code_symbols)
        self.fitness = [0]*len(self.pop)
        self.generation = 0



    def test_pop(self):
        """ """
        base_fit = [self.fitness_function(code) for code in self.pop]

        # code length does affect fitness, but it is easier
        # to factor that in here rather than within the fitness_function
        lengths = [ len(code) for code in self.pop ]

        # normalization factors
        Fma = max(base_fit)
        Fmi = min(base_fit)
        fd = 1./(Fma-Fmi) if Fma != Fmi else 1.
        ld = 1./max(lengths)

        # update
        for i, (f, l) in enumerate(zip(base_fit, lengths)):
            self.fitness[i] = (f-Fmi) * fd * .8 ** (l*ld)



    def pick_fit_parent(self):
        """ """
        # random choice weigthed on fitness
        r = random.random()*sum(self.fitness)
        for code, fitness in zip(self.pop, self.fitness):
            r -= fitness
            if r <= 0:
                return code
        return random.choice(self.pop)



    def recombine_from_parents(self, parents_cnt=2):
        """ """
        son = []

        for i in xrange(parents_cnt):
            blocks = self.pick_fit_parent().split(self.break_symbol)
            son += random.sample(blocks, (len(blocks) / parents_cnt) or 1)

        # duplicate blocks, lose blocks
#        if random.random() < .002:
#            son.pop(random.randrange(len(son)))
#        if random.random() < .002:
#            son.append(random.choice(son))

        return self.break_symbol.join(son)



    def add_random_errors(self, code, mutation_chance=.01):
        """ """
        # the correct way to do this would be to iterate random
        # on every symbol of code, but it would be too slow and
        # probably not that random.
        # So I will just invoke the Law of Big Numbers and
        # assume that the actual number of mutations matches
        # exactly its expected value.

        length = len(code)
        lc = list(code)
        mutations_number = int(  length * mutation_chance  ) or 1

        for i in xrange(mutations_number):
            lc[random.randrange(length)] = random.choice(self.code_symbols)

        return ''.join(lc)





    def move_to_next_generation(self, elders_ratio=.05):
        """ """
        size = len(self.pop)
        elders_cnt = 0 #int( size * elders_ratio)
        youths_cnt = size - elders_cnt

        # extract elders
        best = sorted(zip(self.fitness, self.pop), reverse=True) #[:elders_cnt]
        #elders = zip(*best)[1]

        # produce youths
        youths = [ self.add_random_errors(self.recombine_from_parents()) for i in xrange(youths_cnt)]

        # done
        self.generation += 1
        self.pop = youths #+ list(elders) + youths

        # provide best individual
        return best[0]



    def iterate(self):
        """ """
        self.test_pop()
        return self.move_to_next_generation()





#==============================================================================

def main():
    """
    Simple test for the whole trap.

    """

    symbols = 'abcde'
    stop = 'a'

    def fit(code):
        d = {
            'bb': +1,
            'bbb':+3,
            'ccccc': +6,
            'ddd': +4,
        }

        return sum( v*code.count(k) for k,v in d.items() ) - len(code)

    pop = evolution.create_initial_pop(symbols, 20)

    ev = evolution(fit, symbols, stop)
    for i in xrange(200):
        print ev.iterate()[0], ev.generation

    best = sorted(zip(ev.fitness, ev.pop), reverse=True)[0][1]
    print best


if __name__ == '__main__':
    main()


#EOF