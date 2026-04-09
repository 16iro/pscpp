#include <bits/stdc++.h>
using namespace std;

set<int> POTset;
uint64_t POTmatrix[50][5][5] = {
    0,
};
uint64_t matrix[50][5][5] = {
    0,
};

int NPOT2POT(uint64_t npot) {
    int biggestbit = 0;
    for (int bit = 0; bit < sizeof(uint64_t) * 8; bit++) {
        if ((npot & (uint64_t)(0x01) << bit) > 0) {
            POTset.insert(bit + 1);
            if (bit >= biggestbit)
                biggestbit = bit;
        }
    }
    return biggestbit + 1;
}

void powMatrix(int i, int N) {
    for (int ny = 0; ny < N; ny++) {
        for (int nx = 0; nx < N; nx++) {
            for (int n = 0; n < N; n++) {
                POTmatrix[i][ny][nx] += POTmatrix[i - 1][ny][n] * POTmatrix[i - 1][n][nx];
            }
            POTmatrix[i][ny][nx] %= 1000;
        }
    }
}

void solve() {
    int N;
    uint64_t B;
    cin >> N >> B;
    int maxbit = NPOT2POT(B);

    for (int ny = 0; ny < N; ny++) {
        for (int nx = 0; nx < N; nx++) {
            int number;
            cin >> number;
            POTmatrix[1][ny][nx] = number;
        }
    }

    // pot
    for (int i = 2; i <= maxbit; i++) {
        powMatrix(i, N);
    }

    // mult npot dividees
    for (int n = 0; n < N; n++) {
        matrix[0][n][n] = 1;  // eigenvalued
    }
    int idx = 1;
    for (auto itr = POTset.begin(); itr != POTset.end(); itr++) {
        for (int ny = 0; ny < N; ny++) {
            for (int nx = 0; nx < N; nx++) {
                for (int n = 0; n < N; n++) {
                    int bit = *itr;
                    matrix[idx][ny][nx] += matrix[idx - 1][n][nx] * POTmatrix[bit][ny][n];
                }
                matrix[idx][ny][nx] %= 1000;
            }
        }
        idx++;
    }

    // cout
    idx--;
    for (int ny = 0; ny < N; ny++) {
        for (int nx = 0; nx < N; nx++) {
            cout << matrix[idx][ny][nx];
            if (nx < N - 1)
                cout << " ";
        }
        if (ny < N - 1)
            cout << "\n";
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();

    return 0;
}
