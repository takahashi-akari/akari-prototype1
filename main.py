# Akari Prototype 001
# Description: Compile and run test programs for Intel Intrinsic functions for each architecture on the server for each architecture.
# Author: Takahashi Akari <akaritakahashioss@gmail.com>
# Date: 2023/03/21
# License: MIT License

from fabric import Connection
import itertools


def run_test(connection, architecture, input1, input2, source_code):
    # リモートサーバーにソースコードをアップロード
    with open(f'source_{architecture}.c', 'w') as source_file:
        source_file.write(source_code)
    connection.put(f'source_{architecture}.c', f'source_{architecture}.c')

    # コンパイルコマンドで最適化を行う
    compile_command = f'gcc source_{architecture}.c -o test_{architecture}'
    connection.run(compile_command)

    # テストプログラムを実行し、結果を表示
    result = connection.run(f'./test_{architecture}')
    print(f'Input1: {a[0]}, {a[1]}, {a[2]}, {a[3]}'.format(
        a=[input1[0], input1[1], input1[2], input1[3]]))
    print(f'Input2: {b[0]}, {b[1]}, {b[2]}, {b[3]}'.format(
        b=[input2[0], input2[1], input2[2], input2[3]]))
    # Expect
    print(f'Expect: {a[0] + b[0]}, {a[1] + b[1]}, {a[2] + b[2]}, {a[3] + b[3]}'.format(
        a=[input1[0], input1[1], input1[2], input1[3]], b=[input2[0], input2[1], input2[2], input2[3]]))
    # Result
    print(f'Result {architecture}: {result.stdout.strip()}')


# リモートサーバーの接続情報
servers = {
    'intel': {'host': 'intel_server', 'user': 'username', 'password': 'password'},
    'arm': {'host': 'arm_server', 'user': 'username', 'password': 'password'},
    'riscv': {'host': 'riscv_server', 'user': 'username', 'password': 'password'}
}

# 各サーバーでテストを実行
for arch, server_info in servers.items():
    connection = Connection(
        server_info['host'], user=server_info['user'], password=server_info['password'])
    # 入力値を設定
    # aは0〜10の整数を4つの順列組み合わせ
    a = list(itertools.permutations([i for i in range(1, 11)], 4))
    # bは0〜10の整数を4つの順列組み合わせ
    b = list(itertools.permutations([i for i in range(1, 11)], 4))
    # Intel Intrinsic関数のテストコード
    for aa, bb in zip(a, b):
        source_code = {
            'intel': '''
        #include <iostream>
        #include <stdio.h>
        #include <emmintrin.h>

        int main() {
            __m128i a = _mm_set_epi32({a[0]}, {a[1]}, {a[2]}, {a[3]});
            __m128i b = _mm_set_epi32({b[0]}, {b[1]}, {b[2]}, {b[3]});
            __m128i c = _mm_add_epi32(a, b);

            int result[4];
            _mm_storeu_si128((__m128i *)&result, c);

            printf("Results: %d %d %d %d\n", result[0], result[1], result[2], result[3]);
            return 0;
        '''.format(a=[aa[i][0], aa[i][1], aa[i][2], aa[i][2]], b=[bb[i][0], bb[i][1], bb[i][2], bb[i][2]]),
            'arm': '''
        #include <stdio.h>
        #include <arm_neon.h>

        int main() {
            int32x4_t a = {a[0]}, {a[1]}, {a[2]}, {a[3]}};
            int32x4_t b = {b[0]}, {b[1]}, {b[2]}, {b[3]}};
            int32x4_t c = vaddq_s32(a, b);

            int result[4];
            vst1q_s32(result, c);

            printf("Results: %d %d %d %d\\n", result[0], result[1], result[2], result[3]);
            return 0;
        }
        '''.format(a=[aa[i][0], aa[i][1], aa[i][2], aa[i][2]], b=[bb[i][0], bb[i][1], bb[i][2], bb[i][2]]),
            'riscv': '''
        #include <stdio.h>
        #include <riscv_vector.h>

        int main() {
            int a[4] = {1, 2, 3, 4};
            int b[4] = {5, 6, 7, 8};
            int c[4];

            vint32m1_t va, vb, vc;
            va = vle32_v_i32m1(a);
            vb = vle32_v_i32m1(b);
            vc = vadd_vv_i32m1(va, vb);
            vse32_v_i32m1(c, vc);

            printf("Results: %d %d %d %d\\n", c[0], c[1], c[2], c[3]);
            return 0;
        '''.format(a=[aa[i][0], aa[i][1], aa[i][2], aa[i][2]], b=[bb[i][0], bb[i][1], bb[i][2], bb[i][2]]),
        }
        run_test(connection, arch, aa, bb, source_code[arch])
