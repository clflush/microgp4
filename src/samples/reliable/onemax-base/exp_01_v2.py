# -*- coding: utf-8 -*-
#############################################################################
#          __________                                                       #
#   __  __/ ____/ __ \__ __   This file is part of MicroGP4 v1.0a1 "Kiwi"   #
#  / / / / / __/ /_/ / // /   (!) by Giovanni Squillero and Alberto Tonda   #
# / /_/ / /_/ / ____/ // /_   https://github.com/squillero/microgp4         #
# \__  /\____/_/   /__  __/                                                 #
#   /_/ --MicroGP4-- /_/      "You don't need a big goal, be μ-ambitious!!" #
#                                                                           #
#############################################################################

# Copyright 2019 Giovanni Squillero and Alberto Tonda
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
import sys

import microgp as ugp
from microgp.utils import logging

if __name__ == "__main__":
    ugp.banner()

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="count", default=0, help="increase log verbosity")
    parser.add_argument("-d",
                        "--debug",
                        action="store_const",
                        dest="verbose",
                        const=2,
                        help="log debug messages (same as -vv)")
    args = parser.parse_args()

    if args.verbose == 0:
        ugp.logging.DefaultLogger.setLevel(level=ugp.logging.INFO)
    elif args.verbose == 1:
        ugp.logging.DefaultLogger.setLevel(level=ugp.logging.VERBOSE)
    elif args.verbose > 1:
        ugp.logging.DefaultLogger.setLevel(level=ugp.logging.DEBUG)
        ugp.logging.debug("Verbose level set to DEBUG")

    ugp.logging.cpu_info("Program started")

    # Delete old solutions
    ugp.delete_solutions()

    # Define a parameter of type ugp.parameter.Categorical that can take two values: 0 or 1
    bit = ugp.make_parameter(ugp.parameter.Categorical, alternatives=[0, 1])
    # Define a macro that contains a parameter of type ugp.parameter.Categorical
    word_macro = ugp.Macro("{bit}", {'bit': bit})
    # Create a section containing 8 macros
    word_section = ugp.make_section(word_macro, size=(8, 8), name='word_sec')

    # Create a constraints library
    library = ugp.Constraints()
    library['main'] = ["Bitstring:", word_section]

    # Define the evaluator and the fitness type_________________________________________________________________________
    def my_script(data: str):
        count = data.count('1')
        return list(str(count))

    library.evaluator = ugp.fitness.make_evaluator(evaluator=my_script, fitness_type=ugp.fitness.Lexicographic)

    # Create a list of operators with their arities_____________________________________________________________________
    operators = ugp.Operators()
    # Add initialization operators
    operators += ugp.GenOperator(ugp.create_random_individual, 0)
    # Add mutation operators
    operators += ugp.GenOperator(ugp.hierarchical_mutation, 1)
    operators += ugp.GenOperator(ugp.flat_mutation, 1)
    # Add crossover operators
    operators += ugp.GenOperator(ugp.macro_pool_one_cut_point_crossover, 2)
    operators += ugp.GenOperator(ugp.macro_pool_uniform_crossover, 2)

    # Create the object that will manage the evolution__________________________________________________________________
    mu = 10
    nu = 20
    sigma = 0.7
    lambda_ = 7
    max_age = 10

    darwin = ugp.Darwin(
        constraints=library,
        operators=operators,
        mu=mu,
        nu=nu,
        lambda_=lambda_,
        sigma=sigma,
        max_age=max_age,
    )

    # Evolve____________________________________________________________________________________________________________
    darwin.evolve()
    logging.bare("This is the final population:")
    for individual in darwin.population:
        msg = f"Solution {str(individual.id)} "
        ugp.print_individual(individual, msg=msg, plot=True)
        ugp.logging.bare(f"Fitness: {individual.fitness}")
        ugp.logging.bare("")

    # Print best individuals
    ugp.print_individual(darwin.archive.individuals, msg="These are the best ever individuals:", plot=True)

    ugp.delete_solutions()

    ugp.logging.cpu_info("Program completed")
    sys.exit(0)