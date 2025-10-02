# gp/operators.py

import random

from deap import gp

from src.configs.gp_configs import MAX_MUTATION_DEPTH


def custom_crossover(ind1, ind2):
    """매수/매도 로직을 분리하여 교차"""
    if (
        len(ind1) < 2
        or len(ind2) < 2
        or ind1[0].name != "Strategy"
        or ind2[0].name != "Strategy"
    ):
        return ind1, ind2

    if random.random() < 0.5:
        # 매수 서브트리 교차
        slice1, slice2 = ind1.searchSubtree(1), ind2.searchSubtree(1)
        sub_tree1, sub_tree2 = gp.PrimitiveTree(ind1[slice1]), gp.PrimitiveTree(
            ind2[slice2]
        )
        gp.cxOnePoint(sub_tree1, sub_tree2)
        ind1[slice1], ind2[slice2] = sub_tree1, sub_tree2
    else:
        # 매도 서브트리 교차
        buy_slice1, buy_slice2 = ind1.searchSubtree(1), ind2.searchSubtree(1)
        sub_tree1, sub_tree2 = gp.PrimitiveTree(
            ind1[buy_slice1.stop :]
        ), gp.PrimitiveTree(ind2[buy_slice2.stop :])
        gp.cxOnePoint(sub_tree1, sub_tree2)
        ind1[buy_slice1.stop :], ind2[buy_slice2.stop :] = sub_tree1, sub_tree2

    return ind1, ind2


def custom_mutation(individual, pset):
    """매수/매도 서브트리 내에서 타입에 맞게 변이"""
    if len(individual) < 2 or individual[0].name != "Strategy":
        return (individual,)

    subtree_slice = (
        individual.searchSubtree(1)
        if random.random() < 0.5
        else slice(individual.searchSubtree(1).stop, len(individual))
    )
    selected_subtree_list = individual[subtree_slice]
    if not selected_subtree_list:
        return (individual,)

    temp_tree = gp.PrimitiveTree(selected_subtree_list)
    index = random.randrange(len(temp_tree))
    node = temp_tree[index]

    new_expr = gp.genHalfAndHalf(pset, 1, MAX_MUTATION_DEPTH, type_=node.ret)

    temp_tree[temp_tree.searchSubtree(index)] = new_expr
    individual[subtree_slice] = temp_tree

    return (individual,)
