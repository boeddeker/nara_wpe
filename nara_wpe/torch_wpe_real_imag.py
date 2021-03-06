import numpy as np
import torch
import torch_complex.functional
from torch_complex.tensor import ComplexTensor
from nara_wpe.torch_wpe import build_y_tilde as _build_y_tilde


def build_y_tilde(Y, taps, delay):
    """

    Note: The returned y_tilde consumes a similar amount of memory as Y, because
        of tricks with strides. Usually the memory consumprion is K times
        smaller than the memory consumprion of a contignous array,

    >>> T, D = 20, 2

    # >>> Y = torch.arange(start=1, end=T * D + 1).to(dtype=torch.complex128).reshape([T, D]).t()

    >>> Y = torch.arange(start=1, end=T * D + 1).reshape([T, D]).t()
    >>> Y = ComplexTensor(Y, Y)
    >>> print(Y.numpy())
    [[ 1. +1.j  3. +3.j  5. +5.j  7. +7.j  9. +9.j 11.+11.j 13.+13.j 15.+15.j
      17.+17.j 19.+19.j 21.+21.j 23.+23.j 25.+25.j 27.+27.j 29.+29.j 31.+31.j
      33.+33.j 35.+35.j 37.+37.j 39.+39.j]
     [ 2. +2.j  4. +4.j  6. +6.j  8. +8.j 10.+10.j 12.+12.j 14.+14.j 16.+16.j
      18.+18.j 20.+20.j 22.+22.j 24.+24.j 26.+26.j 28.+28.j 30.+30.j 32.+32.j
      34.+34.j 36.+36.j 38.+38.j 40.+40.j]]
    >>> taps, delay = 4, 2
    >>> Y_tilde = build_y_tilde(Y, taps, delay)
    >>> print(Y_tilde.shape, (taps*D, T))
    torch.Size([8, 20]) (8, 20)
    >>> print(Y_tilde.numpy())
    [[ 0. +0.j  0. +0.j  0. +0.j  0. +0.j  0. +0.j  1. +1.j  3. +3.j  5. +5.j
       7. +7.j  9. +9.j 11.+11.j 13.+13.j 15.+15.j 17.+17.j 19.+19.j 21.+21.j
      23.+23.j 25.+25.j 27.+27.j 29.+29.j]
     [ 0. +0.j  0. +0.j  0. +0.j  0. +0.j  0. +0.j  2. +2.j  4. +4.j  6. +6.j
       8. +8.j 10.+10.j 12.+12.j 14.+14.j 16.+16.j 18.+18.j 20.+20.j 22.+22.j
      24.+24.j 26.+26.j 28.+28.j 30.+30.j]
     [ 0. +0.j  0. +0.j  0. +0.j  0. +0.j  1. +1.j  3. +3.j  5. +5.j  7. +7.j
       9. +9.j 11.+11.j 13.+13.j 15.+15.j 17.+17.j 19.+19.j 21.+21.j 23.+23.j
      25.+25.j 27.+27.j 29.+29.j 31.+31.j]
     [ 0. +0.j  0. +0.j  0. +0.j  0. +0.j  2. +2.j  4. +4.j  6. +6.j  8. +8.j
      10.+10.j 12.+12.j 14.+14.j 16.+16.j 18.+18.j 20.+20.j 22.+22.j 24.+24.j
      26.+26.j 28.+28.j 30.+30.j 32.+32.j]
     [ 0. +0.j  0. +0.j  0. +0.j  1. +1.j  3. +3.j  5. +5.j  7. +7.j  9. +9.j
      11.+11.j 13.+13.j 15.+15.j 17.+17.j 19.+19.j 21.+21.j 23.+23.j 25.+25.j
      27.+27.j 29.+29.j 31.+31.j 33.+33.j]
     [ 0. +0.j  0. +0.j  0. +0.j  2. +2.j  4. +4.j  6. +6.j  8. +8.j 10.+10.j
      12.+12.j 14.+14.j 16.+16.j 18.+18.j 20.+20.j 22.+22.j 24.+24.j 26.+26.j
      28.+28.j 30.+30.j 32.+32.j 34.+34.j]
     [ 0. +0.j  0. +0.j  1. +1.j  3. +3.j  5. +5.j  7. +7.j  9. +9.j 11.+11.j
      13.+13.j 15.+15.j 17.+17.j 19.+19.j 21.+21.j 23.+23.j 25.+25.j 27.+27.j
      29.+29.j 31.+31.j 33.+33.j 35.+35.j]
     [ 0. +0.j  0. +0.j  2. +2.j  4. +4.j  6. +6.j  8. +8.j 10.+10.j 12.+12.j
      14.+14.j 16.+16.j 18.+18.j 20.+20.j 22.+22.j 24.+24.j 26.+26.j 28.+28.j
      30.+30.j 32.+32.j 34.+34.j 36.+36.j]]
    >>> Y_tilde = build_y_tilde(Y, taps, 0)
    >>> print(Y_tilde.shape, (taps*D, T), Y_tilde.real.stride(), Y_tilde.imag.stride())
    torch.Size([8, 20]) (8, 20) (1, 2) (1, 2)
    >>> print('Pseudo size:', np.prod(Y_tilde.size()) * Y_tilde.real.element_size(), np.prod(Y_tilde.size()) * Y_tilde.imag.element_size())
    Pseudo size: 1280 1280
    >>> print('Reak size:', Y_tilde.real.storage().size() * Y_tilde.real.storage().element_size(), Y_tilde.imag.storage().size() * Y_tilde.imag.storage().element_size())
    Reak size: 368 368
    >>> print(Y_tilde.numpy())
    [[ 0. +0.j  0. +0.j  0. +0.j  1. +1.j  3. +3.j  5. +5.j  7. +7.j  9. +9.j
      11.+11.j 13.+13.j 15.+15.j 17.+17.j 19.+19.j 21.+21.j 23.+23.j 25.+25.j
      27.+27.j 29.+29.j 31.+31.j 33.+33.j]
     [ 0. +0.j  0. +0.j  0. +0.j  2. +2.j  4. +4.j  6. +6.j  8. +8.j 10.+10.j
      12.+12.j 14.+14.j 16.+16.j 18.+18.j 20.+20.j 22.+22.j 24.+24.j 26.+26.j
      28.+28.j 30.+30.j 32.+32.j 34.+34.j]
     [ 0. +0.j  0. +0.j  1. +1.j  3. +3.j  5. +5.j  7. +7.j  9. +9.j 11.+11.j
      13.+13.j 15.+15.j 17.+17.j 19.+19.j 21.+21.j 23.+23.j 25.+25.j 27.+27.j
      29.+29.j 31.+31.j 33.+33.j 35.+35.j]
     [ 0. +0.j  0. +0.j  2. +2.j  4. +4.j  6. +6.j  8. +8.j 10.+10.j 12.+12.j
      14.+14.j 16.+16.j 18.+18.j 20.+20.j 22.+22.j 24.+24.j 26.+26.j 28.+28.j
      30.+30.j 32.+32.j 34.+34.j 36.+36.j]
     [ 0. +0.j  1. +1.j  3. +3.j  5. +5.j  7. +7.j  9. +9.j 11.+11.j 13.+13.j
      15.+15.j 17.+17.j 19.+19.j 21.+21.j 23.+23.j 25.+25.j 27.+27.j 29.+29.j
      31.+31.j 33.+33.j 35.+35.j 37.+37.j]
     [ 0. +0.j  2. +2.j  4. +4.j  6. +6.j  8. +8.j 10.+10.j 12.+12.j 14.+14.j
      16.+16.j 18.+18.j 20.+20.j 22.+22.j 24.+24.j 26.+26.j 28.+28.j 30.+30.j
      32.+32.j 34.+34.j 36.+36.j 38.+38.j]
     [ 1. +1.j  3. +3.j  5. +5.j  7. +7.j  9. +9.j 11.+11.j 13.+13.j 15.+15.j
      17.+17.j 19.+19.j 21.+21.j 23.+23.j 25.+25.j 27.+27.j 29.+29.j 31.+31.j
      33.+33.j 35.+35.j 37.+37.j 39.+39.j]
     [ 2. +2.j  4. +4.j  6. +6.j  8. +8.j 10.+10.j 12.+12.j 14.+14.j 16.+16.j
      18.+18.j 20.+20.j 22.+22.j 24.+24.j 26.+26.j 28.+28.j 30.+30.j 32.+32.j
      34.+34.j 36.+36.j 38.+38.j 40.+40.j]]


    The first columns are zero because of the delay.

    """
    if isinstance(Y, ComplexTensor):
        return ComplexTensor(
            _build_y_tilde(Y.real, taps, delay),
            _build_y_tilde(Y.imag, taps, delay),
        )
    else:
        return _build_y_tilde(Y, taps, delay)


def get_power_inverse(signal, psd_context=0):
    """
    Assumes single frequency bin with shape (D, T).

    # >>> s = 1 / torch.tensor([np.arange(1, 6).astype(np.complex128)]*3)
    >>> s = 1 / torch.tensor([np.arange(1, 6).astype(np.float64)]*3)
    >>> s = ComplexTensor(s, -s)
    >>> get_power_inverse(s).numpy()
    array([ 0.5,  2. ,  4.5,  8. , 12.5])
    >>> get_power_inverse(s * 0 + 1, 1).numpy()
    array([1., 1., 1., 1., 1.])
    >>> get_power_inverse(s, 1).numpy()
    array([ 1.6       ,  2.20408163,  7.08196721, 14.04421326, 19.51219512])
    >>> get_power_inverse(s, np.inf).numpy()
    array([1.708104, 1.708104, 1.708104, 1.708104, 1.708104])
    """
    if isinstance(signal, ComplexTensor):
        power = torch.mean(signal.real ** 2 + signal.imag **2, dim=-2)
    else:
        power = torch.mean(torch.abs(signal) ** 2, dim=-2)

    if np.isposinf(psd_context):
        # raise NotImplementedError(psd_context)
        power, _ = torch.broadcast_tensors(torch.mean(power, dim=-1, keepdims=True), power)
    elif psd_context > 0:
        raise NotImplementedError(psd_context)
        #     assert int(psd_context) == psd_context, psd_context
        #     psd_context = int(psd_context)
        #     # import bottleneck as bn
        #     # Handle the corner case correctly (i.e. sum() / count)
        #     # Use bottleneck when only left context is requested
        #     # power = bn.move_mean(power, psd_context*2+1, min_count=1)
        #     power = window_mean(power, (psd_context, psd_context))
    elif psd_context == 0:
        pass
    else:
        raise ValueError(psd_context)
    eps = 1e-10 * torch.max(power)
    inverse_power = 1 / torch.max(power, eps)
    return inverse_power


def hermite(x):
    return x.transpose(-2, -1).conj()

def transpose(x):
    return x.transpose(-2, -1)

def ComplexTensor_to_Tensor(t):
    """
    Converts a third party complex tensor to a native complex torch tensor.

    >>> t = ComplexTensor(np.array([1., 2, 3]))
    >>> t
    ComplexTensor(
        real=tensor([1., 2., 3.], dtype=torch.float64),
        imag=tensor([0., 0., 0.], dtype=torch.float64),
    )
    >>> ComplexTensor_to_Tensor(t)
    tensor([(1.+0.j), (2.+0.j), (3.+0.j)], dtype=torch.complex128)
    """
    assert isinstance(t, ComplexTensor), type(t)
    return t.real + 1j * t.imag


def Tensor_to_ComplexTensor(t):
    """
    Converts a native complex torch tensor to a third party complex tensor.

    >>> t = torch.tensor(np.array([1., 2, 3]) + 0 * 1j)
    >>> t
    tensor([(1.+0.j), (2.+0.j), (3.+0.j)], dtype=torch.complex128)
    >>> Tensor_to_ComplexTensor(t)
    ComplexTensor(
        real=tensor([1., 2., 3.], dtype=torch.float64),
        imag=tensor([0., 0., 0.], dtype=torch.float64),
    )
    """
    assert isinstance(t, torch.Tensor), type(t)
    return ComplexTensor(t.real, t.imag)


def _solve(R, P, solver='torch_complex.solve'):
    if isinstance(R, ComplexTensor):
        if solver == 'torch.solve':
            R = ComplexTensor_to_Tensor(R)
            P = ComplexTensor_to_Tensor(P)

            G, _ = torch.solve(P, R)
            G = Tensor_to_ComplexTensor(G)
        elif solver == 'torch.inverse':
            R = ComplexTensor_to_Tensor(R)
            G = Tensor_to_ComplexTensor(R.inverse()) @ P
        elif solver == 'torch_complex.inverse':
            G = R.inverse() @ P
        elif solver == 'torch_complex.solve':
            G, _ = torch_complex.functional.solve(P, R)
        else:
            raise ValueError(solver)
    else:
        G, _ = torch.solve(P, R)
    return G


def wpe_v6(Y, taps=10, delay=3, iterations=3, psd_context=0, statistics_mode='full',
           solver='torch_complex.solve'):
    """
    This function in similar to nara_wpe.wpe.wpe_v6, but works for torch.
    In particular it is designed for a `torch_complex.tensor.ComplexTensor`.
    The `torch_complex.tensor.ComplexTensor` is used, because at the time
    this code was written, torch had no complete support for complex numbers.

    In 1.6.0.dev20200623 is partial support for complex numbers.
    In this version torch.solve is implemented, but not torch.matmul.
    You can change the `solver` only when partial complex support is given.

    With `solver="torch.solve"` you can use `torch.solve`. Some experiments
    have shown, that the native solver is more robust to find the correct
    solution, compared to the fallback to do the inversion with real numbers.

    >>> T = np.random.randint(100, 120)
    >>> D = np.random.randint(2, 8)
    >>> K = np.random.randint(3, 5)
    >>> K = 2
    >>> delay = np.random.randint(0, 2)

    >>> kwargs = dict(taps=K, delay=delay, iterations=1, statistics_mode='full', psd_context=np.inf)
    
    # Real test:
    >>> Y = np.random.normal(size=(D, T))
    >>> from nara_wpe import wpe as np_wpe
    >>> desired = np_wpe.wpe_v6(Y, **kwargs)
    >>> actual = wpe_v6(torch.tensor(Y), **kwargs).numpy()
    >>> np.testing.assert_allclose(actual, desired, atol=1e-6)

    # Complex test:
    >>> Y = np.random.normal(size=(D, T)) + 1j * np.random.normal(size=(D, T))
    >>> from nara_wpe import wpe as np_wpe
    >>> desired = np_wpe.wpe_v6(Y, **kwargs)
    >>> actual = wpe_v6(ComplexTensor(Y.real, Y.imag), **kwargs).numpy()

    >>> np.testing.assert_allclose(actual, desired, atol=1e-6)
    
    >>> ComplexTensor(Y.real, Y.imag).real.dtype
    torch.float64
    >>> actual1 = wpe_v6(ComplexTensor(Y.real, Y.imag), **kwargs, solver='torch_complex.inverse').numpy()
    >>> np.testing.assert_allclose(actual1, desired, atol=1e-6)
    >>> actual2 = wpe_v6(ComplexTensor(Y.real, Y.imag), **kwargs, solver='torch.solve').numpy()
    >>> np.testing.assert_allclose(actual2, desired, atol=1e-6)
    >>> np.testing.assert_allclose(actual1, actual2, atol=1e-6)

    """
    if statistics_mode == 'full':
        s = Ellipsis
    elif statistics_mode == 'valid':
        s = (Ellipsis, slice(delay + taps - 1, None))
    else:
        raise ValueError(statistics_mode)

    X = Y.clone()
    Y_tilde = build_y_tilde(Y, taps, delay)
    for iteration in range(iterations):
        inverse_power = get_power_inverse(X, psd_context=psd_context)
        Y_tilde_inverse_power = Y_tilde * inverse_power[..., None, :]
        R = Y_tilde_inverse_power[s] @ hermite(Y_tilde[s])
        P = Y_tilde_inverse_power[s] @ hermite(Y[s])
        # G = _stable_solve(R, P)
        G = _solve(R=R, P=P, solver=solver)
        X = Y - hermite(G) @ Y_tilde

    return X


def wpe_step_v1(Y, inverse_power, taps=10, delay=3,
             statistics_mode='full',
             solver='torch_complex.solve'):
    """

    Args:
        Y: (..., channel, frames)
        inverse_power:
        taps:
        delay:
        statistics_mode:
        solver:

    Returns:

    """
    if statistics_mode == 'full':
        s = Ellipsis
    elif statistics_mode == 'valid':
        raise NotImplementedError(statistics_mode)
        s = (Ellipsis, slice(delay + taps - 1, None))
    else:
        raise ValueError(statistics_mode)

    if isinstance(Y, np.ndarray):
        Y = ComplexTensor(Y)
        Y = Y.to(inverse_power.device)

    Y_tilde = build_y_tilde(Y, taps, delay)
    Y_tilde = Y_tilde  # .contiguous()

    Y_tilde_inverse_power = Y_tilde * inverse_power[..., None, :]
    R = Y_tilde_inverse_power[s] @ hermite(Y_tilde[s])
    P = Y_tilde_inverse_power[s] @ hermite(Y[s])

    G = _solve(R=R, P=P, solver=solver)
    
    X = Y - hermite(G) @ Y_tilde

    return X

def wpe_step_v2(Y, inverse_power, taps=10, delay=3,
             statistics_mode='full',
             solver='torch_complex.solve'):
    """

    Args:
        Y: (..., channel, frames)
        inverse_power:
        taps:
        delay:
        statistics_mode:
        solver:

    Returns:

    """
    if statistics_mode == 'full':
        s = Ellipsis
    elif statistics_mode == 'valid':
        raise NotImplementedError(statistics_mode)
        s = (Ellipsis, slice(delay + taps - 1, None))
    else:
        raise ValueError(statistics_mode)

    if isinstance(Y, np.ndarray):
        Y = ComplexTensor(Y)
        Y = Y.to(inverse_power.device)

    Y_tilde = build_y_tilde(Y, taps, delay)

    # Torch does not keep the non contignous property for tensors with for
    # negation (i.e. ComplexTensor.conj changes the sign of imag).
    Y_conj = Y.conj()
    Y_tilde_conj = build_y_tilde(Y_conj, taps, delay)
    # Y_tilde_conj = Y_tilde.conj()

    # This code is faster, but with backward graph the memory consumption is to
    # high. (Pytorch is at the moment not intelligent enough)
    # Y_tilde_inverse_power = Y_tilde * inverse_power[..., None, :]
    # R = Y_tilde_inverse_power[s] @ hermite(Y_tilde[s])
    # P = Y_tilde_inverse_power[s] @ hermite(Y[s])

    import torch.utils.checkpoint

    # remove when https://github.com/pytorch/pytorch/issues/42418
    # has a solution.
    # This may be very expencive, because the calculation of R dominates the
    # execution time of WPE
    def get_R(inverse_power, Y_tilde_real, Y_tilde_imag):
        Y_tilde_real = Y_tilde_real.contiguous()
        Y_tilde_imag = Y_tilde_imag.contiguous()
        Y_tilde = ComplexTensor(Y_tilde_real, Y_tilde_imag)
        Y_tilde_conj = ComplexTensor(Y_tilde_real, -Y_tilde_imag)
        R = torch_complex.functional.einsum(
            '...t,...dt,...et->...de', inverse_power, Y_tilde, Y_tilde_conj)
        return R.real, R.imag

    R = ComplexTensor(*torch.utils.checkpoint.checkpoint(get_R, inverse_power, Y_tilde.real, Y_tilde.imag))

    # print('wpe rss before P', ByteSize(process.memory_info().rss))
    P = torch_complex.functional.einsum(
        '...t,...dt,...et->...de',
        inverse_power, Y_tilde, Y_conj
    )
    G = _solve(R=R, P=P, solver=solver)

    # remove when https://github.com/pytorch/pytorch/issues/42418
    # has a solution.
    def contiguous_einsum(equation, *operands):
        def foo(*operands):
            assert len(operands) % 2 == 0, len(operands)
            operands = [
                ComplexTensor(real.contiguous(), imag.contiguous())
                for real, imag in zip(operands[::2], operands[1::2])
            ]
            ret = torch_complex.functional.einsum(equation, operands)
            return ret.real, ret.imag

        operands = [
            part
            for o in operands
            for part in [o.real, o.imag]
        ]

        real, imag = torch.utils.checkpoint.checkpoint(foo, *operands)
        return ComplexTensor(real, imag)

    # Matmul cannot handle the non contignous Y_tilde, hence use einsum
    # Einsum does not work on the gpu with non contignous, hence use torch.utils.checkpoint.checkpoint
    X = Y - contiguous_einsum('...ij,...ik->...jk', G.conj(), Y_tilde)

    return X

def wpe_step_v3(Y, inverse_power, taps=10, delay=3,
             statistics_mode='full',
             solver='torch_complex.solve'):
    """

    Tested with 1.7.0.dev20200807

    Properties (Compared to lower versions):
      - faster
      - less memory for backward
      - (less peak memory)? Looks so. Difficult to profile.


    Args:
        Y: (..., channel, frames)
        inverse_power:
        taps:
        delay:
        statistics_mode:
        solver:

    Returns:

    """
    if statistics_mode == 'full':
        s = Ellipsis
    elif statistics_mode == 'valid':
        raise NotImplementedError(statistics_mode)
        s = (Ellipsis, slice(delay + taps - 1, None))
    else:
        raise ValueError(statistics_mode)

    if isinstance(Y, np.ndarray):
        Y = ComplexTensor(Y)
        Y = Y.to(inverse_power.device)

    Y_tilde = build_y_tilde(Y, taps, delay)

    # Torch does not keep the non contignous property for tensors with for
    # negation (i.e. ComplexTensor.conj changes the sign of imag).
    Y_conj = Y.conj()
    Y_tilde_conj = build_y_tilde(Y_conj, taps, delay)
    # Y_tilde_conj = Y_tilde.conj()

    # This code is faster, but with backward graph the memory consumption is to
    # high. (Pytorch is at the moment not intelligent enough)
    # Y_tilde_inverse_power = Y_tilde * inverse_power[..., None, :]
    # R = Y_tilde_inverse_power[s] @ transpose(Y_tilde_conj[s])
    # P = Y_tilde_inverse_power[s] @ transpose(Y_conj[s])


    def get_correlation(m, Y1, Y2):
        real = torch.einsum(
            '...t,...dt,...et->...de',
            m, Y1.real, Y2.real
        ) - torch.einsum(
            '...t,...dt,...et->...de',
            m, Y1.imag, Y2.imag
        )

        imag = torch.einsum(
            '...t,...dt,...et->...de',
            m, Y1.real, Y2.imag
        ) + torch.einsum(
            '...t,...dt,...et->...de',
            m, Y1.imag, Y2.real
        )
        return ComplexTensor(real, imag)


    # R_conj = torch_complex.functional.einsum(
    #     '...t,...dt,...et->...de', inverse_power, Y_tilde_conj, Y_tilde)
    R_conj = get_correlation(inverse_power, Y_tilde_conj, Y_tilde)

    # # print('wpe rss before P', ByteSize(process.memory_info().rss))
    # P_conj = torch_complex.functional.einsum(
    #     '...t,...dt,...et->...de',
    #     inverse_power, Y_tilde_conj, Y
    # )
    P_conj = get_correlation(inverse_power, Y_tilde_conj, Y)
    
    G_conj = _solve(R=R_conj, P=P_conj, solver=solver)

    # Matmul converts the non contignous Y_tilde to contignous, hence use einsum
    # Einsum does not work on the gpu with non contignous, hence use torch.utils.checkpoint.checkpoint
    # X = Y - torch_complex.functional.einsum('...ij,...ik->...jk', G_conj, Y_tilde)
    X = ComplexTensor(
        Y.real
        - torch.einsum('...ij,...ik->...jk', G_conj.real, Y_tilde.real)
        + torch.einsum('...ij,...ik->...jk', G_conj.imag, Y_tilde.imag),
        Y.imag
        - torch.einsum('...ij,...ik->...jk', G_conj.real, Y_tilde.imag)
        - torch.einsum('...ij,...ik->...jk', G_conj.imag, Y_tilde.real),
    )

    return X

wpe = wpe_v6
wpe_step = wpe_step_v3