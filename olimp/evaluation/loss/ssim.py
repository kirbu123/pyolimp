from __future__ import annotations

import torch.nn as nn
import torch.nn.functional as F
import torch
from torch import Tensor


class SSIMLoss(nn.Module):
    def __init__(self, kernel_size: int = 11, sigma: float = 1.5) -> None:
        """Computes the structural similarity (SSIM) index map between two images.

        Args:
            kernel_size (int): Height and width of the gaussian kernel.
            sigma (float): Gaussian standard deviation in the x and y direction.
        """

        super().__init__()
        self.kernel_size = kernel_size
        self.sigma = sigma
        self.gaussian_kernel = self._create_gaussian_kernel(
            self.kernel_size, self.sigma
        )

    def forward(self, x: Tensor, y: Tensor, as_loss: bool = True) -> Tensor:

        if not self.gaussian_kernel.is_cuda:
            self.gaussian_kernel = self.gaussian_kernel.to(x.device)

        ssim_map = self._ssim(x, y)

        if as_loss:
            return 1 - ssim_map.mean()
        else:
            return ssim_map

    def _ssim(self, x: Tensor, y: Tensor) -> Tensor:

        # Compute means
        ux = F.conv2d(
            x, self.gaussian_kernel, padding=self.kernel_size // 2, groups=3
        )
        uy = F.conv2d(
            y, self.gaussian_kernel, padding=self.kernel_size // 2, groups=3
        )

        # Compute variances
        uxx = F.conv2d(
            x * x,
            self.gaussian_kernel,
            padding=self.kernel_size // 2,
            groups=3,
        )
        uyy = F.conv2d(
            y * y,
            self.gaussian_kernel,
            padding=self.kernel_size // 2,
            groups=3,
        )
        uxy = F.conv2d(
            x * y,
            self.gaussian_kernel,
            padding=self.kernel_size // 2,
            groups=3,
        )
        vx = uxx - ux * ux
        vy = uyy - uy * uy
        vxy = uxy - ux * uy

        c1 = 0.01**2
        c2 = 0.03**2
        numerator = (2 * ux * uy + c1) * (2 * vxy + c2)
        denominator = (ux**2 + uy**2 + c1) * (vx + vy + c2)
        return numerator / (denominator + 1e-12)

    def _create_gaussian_kernel(
        self, kernel_size: int, sigma: float
    ) -> Tensor:

        start = (1 - kernel_size) / 2
        end = (1 + kernel_size) / 2
        kernel_1d = torch.arange(start, end, step=1, dtype=torch.float)
        kernel_1d = torch.exp(-torch.pow(kernel_1d / sigma, 2) / 2)
        kernel_1d = (kernel_1d / kernel_1d.sum()).unsqueeze(dim=0)

        kernel_2d = torch.matmul(kernel_1d.t(), kernel_1d)
        kernel_2d = kernel_2d.expand(
            3, 1, kernel_size, kernel_size
        ).contiguous()
        return kernel_2d


class ContrastSSIMLoss(nn.Module):
    @staticmethod
    def calculate_contrast_oneimg_l1(img: Tensor, window_size: int) -> Tensor:
        img = img.permute(0, 2, 3, 1)
        x_diff = img[
            :, window_size : 256 - window_size, window_size : 256 - window_size
        ]
        x = x_diff
        # print('2222',x.shape)
        # start = time.time()
        flag = 0
        for i in range(-window_size, window_size + 1):
            for j in range(-window_size, window_size + 1):
                if (i == -window_size) and (j == -window_size):
                    img_diff = (
                        x_diff
                        - img[
                            :,
                            window_size + i : 256 - window_size + i,
                            window_size + j : 256 - window_size + j,
                        ]
                    )
                    img_diff = torch.sum(torch.abs(img_diff), 3)
                    # print(img_diff,img_diff.size())
                    img_diff = torch.unsqueeze(img_diff, 3)
                    x = img_diff
                    flag += 1
                elif (i == 0) and (j == 0):
                    continue
                else:
                    # print(img_diff.shape)
                    flag += 1
                    # print(i, j, flag)
                    img_diff = (
                        x_diff
                        - img[
                            :,
                            window_size + i : 256 - window_size + i,
                            window_size + j : 256 - window_size + j,
                        ]
                    )
                    img_diff = torch.sum(torch.abs(img_diff), 3)
                    img_diff = torch.unsqueeze(img_diff, 3)
                    x = torch.cat((x, img_diff), 3)
        # print(x[1,120,120,:])
        # exit()
        # nrand = np.array([i for i in range(120)])
        # np.random.shuffle(nrand)
        # print(np.random.shuffle(nrand))
        # nrand = nrand[0:60]
        # print(nrand)
        # trand = torch.from_numpy(nrand).type(torch.long)
        # trand = torch.arange(120)
        # trand = torch.randint(0, 120, (60,))
        return torch.abs(x[:, :, :, :120])

    def forward(
        self, original_image: Tensor, simulated_image: Tensor
    ) -> Tensor:
        criterion_contrast = torch.nn.L1Loss()
