function x_normalized = normalize_precoded_signal(precoder, precoder_type, M, s, N_SNR)

    N_BLK = size(s,1);
    
    switch upper(precoder_type)
        case {'ZF', 'MF'}
            x = precoder * s.';
            x_normalized = zeros(size(x));
            for m = 1:M
                Px = norm(x(m, :))^2 / length(x(:,m));
                x_normalized(m, :) = x(m, :) / sqrt(Px);
            end
        case 'MMSE'
            x = zeros(M, N_BLK, N_SNR);
            x_normalized = zeros(M, N_BLK, N_SNR);
            for snr_idx = 1:N_SNR
                x(:,:,snr_idx) = precoder(:,:,snr_idx) * s.';
                for m = 1:M
                    Px = norm(x(m, :, snr_idx))^2 / length(x(:,m, snr_idx));
                    x_normalized(m, :, snr_idx) = x(m, :, snr_idx) / sqrt(Px);
                end
            end
        otherwise
            error('Invalid precoder type. Choose "ZF", "MF", or "MMSE".');
    end
end