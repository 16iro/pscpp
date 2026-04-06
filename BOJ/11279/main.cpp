#include <bits/stdc++.h>
using namespace std;

vector<int> heap;

void push(int input) {
    heap.push_back(input);
    int idx = heap.size() - 1;
    int p_idx = idx / 2;
    while (p_idx < idx) {
        if (heap[p_idx] >= heap[idx]) {
            return;
        }
        swap(heap[p_idx], heap[idx]);
        idx /= 2;
        p_idx /= 2;
    }
}

int pop() {
    if (heap.size() <= 0)
        return 0;
    int result = heap[0];
    swap(heap[0], heap[heap.size() - 1]);
    heap.pop_back();
    int idx = 1;
    int l_idx, r_idx, le_idx;
    while (true) {
        l_idx = (idx * 2) <= (int)heap.size() ? idx * 2 : -1;
        r_idx = (idx * 2 + 1) <= (int)heap.size() ? idx * 2 + 1 : -1;
        if (l_idx == -1 && r_idx == -1) {
            break;
        } else if (l_idx == -1 || r_idx == -1) {
            le_idx = r_idx == -1 ? l_idx : r_idx;
        } else {
            le_idx = heap[l_idx - 1] >= heap[r_idx - 1] ? l_idx : r_idx;
        }

        if (heap[idx - 1] < heap[le_idx - 1]) {
            swap(heap[idx - 1], heap[le_idx - 1]);
            idx = le_idx;
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
