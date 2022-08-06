#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

// node in tree representation of derivative
class Node
{
public:
    
    vector <Node*> nexts;
};

class FuncNode: public Node
{
public:
    int n_args
};

/*
f^g = e^ln(f^g) = e^(g*ln(f))

(f^g)' = ( e^(g*ln(f)) )' = e^(g*ln(f)) * (g*ln(f))' = f^g * (g' * ln(f) + )

*/

