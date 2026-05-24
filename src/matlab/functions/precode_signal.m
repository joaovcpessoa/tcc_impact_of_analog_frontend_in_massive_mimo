function precoder = precode_signal(precoder_type, H, N_SNR, snr)
    
    [M, K] = size(H);
    
    switch upper(precoder_type)
        case 'ZF'
            precoder = conj(H) / (H.' * conj(H));
        case 'MF'
            precoder = conj(H) ./ (vecnorm(H).^2);
        case 'MMSE'
            precoder = zeros(M, K, N_SNR);
            for snr_idx = 1:N_SNR
                precoder(:,:,snr_idx) = conj(H) / (H.' * conj(H) + 1/snr(snr_idx)*eye(K));
            end
        otherwise
            error('Invalid precoder type. Choose "ZF", "MF", or "MMSE".');
    end
end