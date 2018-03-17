import sys
import cv2
import random as rand

import ImageSegmentation as seg
import RegionOperator as ro
import SimilarityOperator as so

def generate_image(img, rgset):
    random_color = lambda: (int(rand.random() * 255), int(rand.random() * 255), int(rand.random() * 255))
    color = [random_color() for i in range(len(rgset))]

    save_img = img.copy()

    for i in range(len(rgset)):
        cv2.rectangle(save_img, (rgset[i].rect.left, rgset[i].rect.top), (rgset[i].rect.right, rgset[i].rect.bottom), color[i], 2)

    return save_img

def main():
    sigma = float(sys.argv[1])
    k = float(sys.argv[2])
    min_size = float(sys.argv[3])
    smallest = int(sys.argv[4])
    largest = int(sys.argv[5])
    distortion = float(sys.argv[6])
    img = cv2.imread(sys.argv[7])

    ufset = seg.segment_image(sigma, k, min_size, img)

    rgset = ro.extract_region(img, ufset)
    nbset = ro.extract_neighbour(rgset)

    height, width, channel = img.shape
    im_size = width * height
    simset = so.calc_init_similarity(rgset, nbset, im_size)

    while simset != []:
        sim_value = lambda element: element[0]
        max_sim_idx = simset.index(max(simset, key=sim_value))

        a = simset[max_sim_idx][1]
        b = simset[max_sim_idx][2]

        rgset.append(ro.merge_region(rgset[a], rgset[b]))

        for sim in simset:
            if sim[1] == a or sim[1] == b or sim[2] == a or sim[2] == b:
                simset.remove(sim)

                if (sim[1] == a and sim[2] == b) or (sim[1] == b and sim[2] == a):
                    continue

                new_a = rgset.index(rgset[-1])
                new_b = sim[2] if sim[1] == a or sim[1] == b else sim[1]
                simset.append((so.calc_similarity(rgset[new_a], rgset[new_b], im_size), new_a, new_b))

    proposal = []

    for rg in rgset:
        if ro.has_same_rect_region(proposal, rg.rect):
            continue
        if rg.size < smallest or rg.size > largest:
            continue
        rg_wh = rg.rect.get_width() / rg.rect.get_height()
        rg_hw = rg.rect.get_height() / rg.rect.get_width()
        if rg_wh > distortion or rg_hw > distortion:
            continue

        proposal.append(rg)

    save_img = generate_image(img, proposal)
    cv2.imwrite(sys.argv[8], save_img)

if __name__ == '__main__':
    main()