function decoder = decode_signal(decoder_type, H, N_SNR, snr)

    [M, K] = size(H);

    switch upper(decoder_type)
        case 'ZF'
            decoder = (H' * conj(H)) \ H';
        case 'MF'
            decoder = H';
        case 'MMSE'
            decoder = zeros(K, M, N_SNR);
            for snr_idx = 1:N_SNR
                decoder(:,:,snr_idx) = pinv(H' * H + (1/snr(snr_idx)) * eye(K)) * H';
            end
        otherwise
            error('Invalid receiver type. Choose "ZF", "MF", or "MMSE".');
    end
end