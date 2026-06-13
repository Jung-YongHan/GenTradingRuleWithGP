# after/gp/operators.py
"""커스텀 교차/변이 연산자.

로직은 원본과 **동일**(동일 난수열 → 재현성 보존). 변이 최대 깊이만 모듈 전역 상수 대신
인자로 받아 설정 객체(GPConfig)에서 주입할 수 있게 했다.
"""

from __future__ import annotations

import random

from deap import gp


def custom_crossover(ind1, ind2):
    """매수/매도 로직을 분리하여 교차."""
    if (
        len(ind1) < 2
        or len(ind2) < 2
        or ind1[0].name != "Strategy"
        or ind2[0].name != "Strategy"
    ):
        return ind1, ind2

    if random.random() < 0.5:
        slice1, slice2 = ind1.searchSubtree(1), ind2.searchSubtree(1)
        sub_tree1 = gp.PrimitiveTree(ind1[slice1])
        sub_tree2 = gp.PrimitiveTree(ind2[slice2])
        gp.cxOnePoint(sub_tree1, sub_tree2)
        ind1[slice1], ind2[slice2] = sub_tree1, sub_tree2
    else:
        buy_slice1, buy_slice2 = ind1.searchSubtree(1), ind2.searchSubtree(1)
        sub_tree1 = gp.PrimitiveTree(ind1[buy_slice1.stop :])
        sub_tree2 = gp.PrimitiveTree(ind2[buy_slice2.stop :])
        gp.cxOnePoint(sub_tree1, sub_tree2)
        ind1[buy_slice1.stop :], ind2[buy_slice2.stop :] = sub_tree1, sub_tree2

    return ind1, ind2


def custom_mutation(individual, pset, max_mutation_depth):
    """매수/매도 서브트리 내에서 타입에 맞게 변이."""
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

    new_expr = gp.genHalfAndHalf(pset, 1, max_mutation_depth, type_=node.ret)

    temp_tree[temp_tree.searchSubtree(index)] = new_expr
    individual[subtree_slice] = temp_tree

    return (individual,)
