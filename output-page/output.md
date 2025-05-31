![](figures/0-0-FIGURE.jpg)

Figure 4. Ablation studies on various datasets in which the number of columns is varied and the aggregator is included or not included. The results generally support the use of more columns and an aggregator module.

| Method AMDCN (without perspective infor-matian)  | MAE 16.6 |
| --- | --- |
| 1I1C星C直直 AMDCN (with perspective information)  | 14.9 |
| 福 LBP+RR 28 (with perspective infor-matian)  | 31.0 |
| Iiitioii MCNN 128 (with perspective information)  | 11.6 |
| 127 (with perspective information | 12.9 |

Table 4. Mean absolute error of vrious methods on WorldExpo crowds

We obtain superior or comparable results in most of these datasets. The AMDCN is capable of outperforming these approaches completely especially when perspective information is not provided, as in UCF and TRANCOS. These results show that the AMDCN performs surprisingly well and is also robust to scale effects. Further, our ablation study of removing the aggregator network shows that using more columns and an aggregator provides the best accuracy for counting -- especially so when there is no perspective information.

## 5.2. Future Work

In addition to an analysis of performance on counting, a density regressor can also be used to locate objects in the image. As mentioned previously, if the regressor is accurate and precise enough, the resulting density map can be used to locate the objects in the image. We expect that in order to do this, one must regress each object to a single point rather than a region specified by a Gaussian. Perhaps this might be

$$
( c ) \ {\mathrm{U C S D ~ o r i g i n a l ~ s p l i t}}
$$

accomplished by applying non-maxima suppression to the final layer activations.

Indeed, the method of applying dilated filters to a multi-column convolutional network in order to enable extracting features of a large number of scales can be applied to various other dense prediction tasks, such as object segmentation at multiple scales or single image depth map prediction. Though we have only conducted experiments on counting and used 5 columns, the architecture presented can be extended and adapted to a variety of tasks that require information at multiple scales.

## Acknowledgment

This material is based upon work supported by the National Science Foundation under Grant No. 1359275 and 1659788. Any opinions, findings, and conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the National Science Foundation. Furthermore, we acknowledge Kyle Yee and Sridhama Prakhya for their helpful conversations and insights during the research process.

## References

[1] S. An, W. Liu, and S. Venkatesh. Face recognition using kernel ridge regression. In Computer Vision and Pattern Recognition, 2007. CVPR'07. IEEE Conference on, pages 1-7. IEEE, 2007.
[2] $\bf c$ . Arteta, V. Lempitsky, J. A. Noble, and A. Zisser-man. Interactive object counting. In European Conference on Computer Vision, pages 504 -518. Springer, 2014.
[3] D. Babu Sam, S. Surya, and R. Venkatesh Babu. Switching convolutional neural network for crowd