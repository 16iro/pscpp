#include <bits/stdc++.h>
using namespace std;

// heap as vector
// 1-23-4567-... pow(2,n-1)~pow(2,n)-1
vector<int> heap;
void push(int input) {
    heap.push_back(input);
    int n_idx = heap.size();
    while (true) {
        if (n_idx - 1 == 0)
            return;
        int p_idx = (n_idx / 2);
        if (heap[p_idx - 1] > heap[n_idx - 1]) {
            swap(heap[p_idx - 1], heap[n_idx - 1]);
        } else
            return;
        n_idx = p_idx;
    }
}

int pop() {
    if (heap.size() <= 0)
        return 0;
    int result = heap[0];
    swap(heap.front(), heap.back());
    heap.pop_back();
    int n_idx = 1;
    while (true) {
        int l_idx = n_idx * 2;
        int r_idx = n_idx * 2 + 1;
        l_idx = l_idx > (int)(heap.size()) ? -1 : l_idx;
        r_idx = r_idx > (int)(heap.size()) ? -1 : r_idx;

        // find LE node
        int ge_idx = -1;
        if (l_idx == -1 && r_idx == -1) {
            break;
        } else if (l_idx == -1 || r_idx == -1) {
            ge_idx = r_idx == -1 ? l_idx : r_idx;
        } else {
            ge_idx = heap[l_idx - 1] <= heap[r_idx - 1] ? l_idx : r_idx;
        }

        // swap if child node is GE than current node
        if (heap[n_idx - 1] >= heap[ge_idx - 1]) {
            swap(heap[n_idx - 1], heap[ge_idx - 1]);
            n_idx = ge_idx;
        } else {
            break;
        }
    }
    return result;
}

void solve() {
    int N;
    cin >> N;

    for (int n = 0; n < N; n++) {
        int input;
        cin >> input;
        if (input == 0) {
            cout << pop() << "\n";
        } else {
            push(input);
        }
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();

    return 0;
}
