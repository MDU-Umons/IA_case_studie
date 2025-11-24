import sys
import subprocess
import pathlib
import os
import json

def ensure_requirements_installed():
    """
    Vérifie que numpy et matplotlib sont installés.
    Si non, lance un pip install -r requirements.txt
    """
    missing = []
    try:
        import numpy  # noqa: F401
    except ImportError:
        missing.append("numpy")

    try:
        import matplotlib  # noqa: F401
    except ImportError:
        missing.append("matplotlib")

    if missing:
        print("Dépendances manquantes :", ", ".join(missing))
        req_path = pathlib.Path(__file__).with_name("requirements.txt")
        if not req_path.exists():
            raise FileNotFoundError(
                f"requirements.txt introuvable à : {req_path}\n"
                "Crée-le (voir instructions) avant de relancer."
            )

        print("Installation des dépendances via requirements.txt ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_path)])
        print("Installation terminée.\n")


# On vérifie/installe AVANT les imports tiers
ensure_requirements_installed()

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Polygon
from matplotlib.path import Path

def get_polygon_from_clicks(
    image,
    title="Cliquez pour ajouter des points (Enter pour valider, Backspace/u pour annuler le dernier, Esc pour tout effacer)",
    overlay_polygons=None,
    line_color="red"
):
    """
    Sélection interactive de points :
    - clic gauche  : ajoute un point
    - Backspace / u: annule le dernier point
    - Enter        : termine et renvoie la liste des points
    - Esc          : efface tout
    Le polygone est affiché fermé (dernier point relié au premier).

    overlay_polygons: liste de dicts {"points": [...], "color": "red"/"white"/...}
                      qui seront dessinés en fond (target + distractors déjà encodés).
    line_color: couleur du polygone en cours de dessin.
    """
    fig, ax = plt.subplots()
    ax.imshow(image)

    # Dessiner les polygones déjà encodés (target + distractors précédents)
    if overlay_polygons:
        for poly in overlay_polygons:
            pts = poly.get("points", [])
            color = poly.get("color", "yellow")
            if not pts:
                continue
            if len(pts) > 1:
                pts_to_draw = pts + [pts[0]]
            else:
                pts_to_draw = pts
            xs, ys = zip(*pts_to_draw)
            ax.plot(xs, ys, "-", color=color, linewidth=2)

    ax.set_title(title)

    points = []
    # ligne qui sera mise à jour au fur et à mesure
    line, = ax.plot([], [], "-b", marker="o")

    done = {"value": False}  # petit conteneur mutable pour passer l'info aux callbacks

    def redraw():
        if points:
            # fermer le polygone en reliant au premier point si > 1
            if len(points) > 1:
                pts_to_draw = points + [points[0]]
            else:
                pts_to_draw = points
            xs, ys = zip(*pts_to_draw)
            line.set_data(xs, ys)
        else:
            line.set_data([], [])
        fig.canvas.draw_idle()

    def on_click(event):
        # on ignore les clics en dehors de l'axe ou si déjà terminé
        if done["value"] or event.inaxes != ax:
            return
        if event.button == 1:  # clic gauche
            x, y = event.xdata, event.ydata
            if x is None or y is None:
                return
            points.append((float(x), float(y)))
            redraw()

    def on_key(event):
        # validation
        if event.key in ("enter", "return"):
            done["value"] = True
            plt.close(fig)

        # Backspace ou 'u' : enlever le dernier point
        elif event.key in ("backspace", "u"):
            if points:
                points.pop()
                redraw()

        # Esc : reset complet
        elif event.key in ("escape", "esc"):
            points.clear()
            redraw()

    cid_click = fig.canvas.mpl_connect("button_press_event", on_click)
    cid_key   = fig.canvas.mpl_connect("key_press_event",   on_key)

    plt.show()

    fig.canvas.mpl_disconnect(cid_click)
    fig.canvas.mpl_disconnect(cid_key)

    return points

def polygons_to_mask(img_shape, polygons):
    """
    Convertit une liste de polygones (liste de points) en masque binaire.
    blanc (255) à l'intérieur, noir (0) ailleurs.
    """
    h, w = img_shape[:2]
    mask = np.zeros((h, w), dtype=bool)

    # grille de pixels (x,y)
    yy, xx = np.mgrid[:h, :w]
    pix = np.vstack((xx.ravel(), yy.ravel())).T  # (N,2)

    for poly in polygons:
        if poly is None or len(poly) < 3:
            continue
        path = Path(poly)
        inside = path.contains_points(pix, radius=0.5).reshape(h, w)
        mask |= inside

    return (mask.astype(np.uint8) * 255)

def save_mask_png(mask, out_path):
    """
    Sauvegarde un masque uint8 (0/255) en PNG.
    """
    mpimg.imsave(out_path, mask, cmap="gray", vmin=0, vmax=255)
    print(f"Masque sauvegardé : {out_path}")

def draw_polygons_on_ax(ax, target_pts, distractors):
    """
    Dessine target (rouge) + distractors (blanc) sur un axe existant.
    """
    if target_pts:
        poly_t = Polygon(target_pts, closed=True, fill=False, edgecolor="red", linewidth=2)
        ax.add_patch(poly_t)

    for dis in distractors:
        pts = dis["points"]
        if not pts:
            continue
        poly_d = Polygon(pts, closed=True, fill=False, edgecolor="white", linewidth=2)
        ax.add_patch(poly_d)

def save_annotated_image(image, target_pts, distractors, out_path):
    fig, ax = plt.subplots()
    ax.imshow(image)
    draw_polygons_on_ax(ax, target_pts, distractors)
    ax.set_axis_off()
    fig.savefig(out_path, bbox_inches="tight", dpi=300)
    plt.close(fig)
    print(f"Image annotée sauvegardée : {out_path}")

def load_annotations(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)

    target_pts = data["target"]["points"]
    distractors = data.get("distractors", [])

    return target_pts, distractors

def finalize_outputs(image, target_points, distractors, base_path_no_ext):
    """
    Calcule masques, sauvegarde masques + image annotée, affiche 3 axes.
    """
    # Masques
    target_mask = polygons_to_mask(image.shape, [target_points])
    distract_mask = polygons_to_mask(image.shape, [d["points"] for d in distractors])

    out_target_mask = base_path_no_ext + "_mask_target.png"
    out_distr_mask  = base_path_no_ext + "_mask_distractors.png"
    save_mask_png(target_mask, out_target_mask)
    save_mask_png(distract_mask, out_distr_mask)

    # Image annotée
    out_annotated = base_path_no_ext + "_annotated.png"
    save_annotated_image(image, target_points, distractors, out_annotated)

    # Affichage 3 axes
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    axes[0].imshow(image)
    draw_polygons_on_ax(axes[0], target_points, distractors)
    axes[0].set_title("Image originale + contours")
    axes[0].set_axis_off()

    axes[1].imshow(target_mask, cmap="gray", vmin=0, vmax=255)
    axes[1].set_title("Masque Target")
    axes[1].set_axis_off()

    axes[2].imshow(distract_mask, cmap="gray", vmin=0, vmax=255)
    axes[2].set_title("Masque Distractors")
    axes[2].set_axis_off()

    plt.tight_layout()
    plt.show()


def main():
    path = "C:/Users/mrgtd/OneDrive - UMONS/MA 2/Q1/IA_case_studie/PixLab"

    # ---- Choix mode ----
    rep_mode = input("As-tu déjà un fichier JSON d'annotations ? (o/n) : ").strip().lower()
    while rep_mode not in ("o", "n"):
        rep_mode = input("Merci de répondre par 'o' (oui) ou 'n' (non) : ").strip().lower()

    # ---- Image ----
    name = input("Nom de l'image png (sans .png) : ").strip()
    path_image = os.path.join(path, name + ".png")
    image = mpimg.imread(path_image)
    base_no_ext = path_image.rsplit(".", 1)[0]

    if rep_mode == "o":
        # ---- Charger JSON existant ----
        json_name = input("Nom du JSON (sans extension) : ").strip()
        json_path = os.path.join(path, json_name + ".json")
        target_points, distractors = load_annotations(json_path)

        print(f"Annotations chargées depuis : {json_path}")

        # ---- Direct to outputs ----
        finalize_outputs(image, target_points, distractors, base_no_ext)
        return

    # ==============================
    # Mode création d'un nouveau JSON
    # ==============================

    # ---- Target ----
    print("\n=== Définition du TARGET ===")
    target_points = get_polygon_from_clicks(
        image,
        "Cliquez pour définir le TARGET (Enter pour valider)"
    )
    target_description = input("Description du target : ")

    # ---- Distractors ----
    distractors = []
    i = 0
    while True:
        rep = input("\nAjouter un distractor ? (o/n) : ").strip().lower()
        while rep not in ("o", "n"):
            rep = input("Merci de répondre par 'o' (oui) ou 'n' (non) : ").strip().lower()

        if rep == "n":
            break

        i += 1
        print(f"\n=== Distractor {i} ===")

        overlay = []
        if target_points:
            overlay.append({"points": target_points, "color": "red"})
        for dis in distractors:
            overlay.append({"points": dis["points"], "color": "white"})

        pts = get_polygon_from_clicks(
            image,
            f"Cliquez pour distractor {i} (Enter pour valider, Backspace/u pour annuler)",
            overlay_polygons=overlay,
            line_color="white"
        )
        desc = input(f"Description du distractor {i} : ")
        distractors.append({
            "points": pts,
            "description": desc
        })

    # ---- Sauvegarde JSON ----
    data = {
        "target": {
            "points": target_points,
            "description": target_description
        },
        "distractors": distractors
    }

    out_json = base_no_ext + "_annotations.json"
    with open(out_json, "w") as f:
        json.dump(data, f, indent=4)
    print(f"\nJSON sauvegardé dans : {out_json}")

    # ---- Outputs (masques + image annotée + affichage) ----
    finalize_outputs(image, target_points, distractors, base_no_ext)

if __name__ == "__main__":
    main()
