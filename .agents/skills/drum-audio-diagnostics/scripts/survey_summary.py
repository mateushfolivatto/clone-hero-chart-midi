# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["numpy==2.3.5", "matplotlib==3.10.8", "mido==1.3.3"]
# ///
"""Summarize a completed frozen survey without changing predictions or labels."""

from __future__ import annotations

import argparse
import base64
import html
import json
from collections import Counter
from pathlib import Path

import chart_reference as shared
import matplotlib.pyplot as plt
from reference_signal import summarize
from survey_statistics import observations, summarize_survey

from drumforge.diagnostics.survey import identity


def render(summary, per_song, destination):
    groups = shared.TARGET_GROUPS
    labels = ["Bumbo", "Caixa aproximada", "Prato amarelo"]
    fig, ax = plt.subplots(figsize=(9, 4), layout="constrained")
    for offset, method in [(-0.18, "baseline"), (0.18, "frozen")]:
        ax.bar(
            [i + offset for i in range(3)],
            [summary["cells"]["mix"][g][method]["f1"] for g in groups],
            width=0.36,
            label="original" if method == "baseline" else "perfil congelado",
        )
    ax.set(
        xticks=range(3),
        xticklabels=labels,
        ylim=(0, 1),
        ylabel="F1 contra o chart",
        title="Mix: mesmas músicas, regras sem recalibração",
    )
    ax.legend()
    ax.grid(axis="y", alpha=0.2)
    fig.savefig(destination / "01-mix.png", dpi=150)
    plt.close(fig)

    hh = [
        r
        for r in per_song
        if r["mode"] == "mix"
        and r["group"] == "YELLOW_CYMBAL_PROXY"
        and r["baseline"]["tp"] + r["baseline"]["fn"] > 0
    ]
    fig, ax = plt.subplots(figsize=(7, 6), layout="constrained")
    ax.scatter([r["baseline"]["f1"] for r in hh], [r["frozen"]["f1"] for r in hh], alpha=0.75)
    ax.plot([0, 1], [0, 1], color="gray", linestyle="--")
    for r in sorted(hh, key=lambda x: abs(x["frozen"]["f1"] - x["baseline"]["f1"]), reverse=True)[
        :5
    ]:
        ax.annotate(r["title"], (r["baseline"]["f1"], r["frozen"]["f1"]), fontsize=7)
    ax.set(
        xlim=(0, 1),
        ylim=(0, 1),
        xlabel="F1 original",
        ylabel="F1 perfil congelado",
        title="Prato amarelo na mix — cada ponto é uma música",
    )
    ax.grid(alpha=0.2)
    fig.savefig(destination / "02-yellow-by-song.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4), layout="constrained")
    for group, label in zip(groups, labels, strict=True):
        item = next(
            p
            for p in summary["paired_sources"]
            if p["left"] == "drums" and p["group"] == group and p["method"] == "frozen"
        )
        n = item["left_metrics"]["songs"]
        ax.plot(
            [0, 1],
            [item["left_metrics"]["f1"], item["right_metrics"]["f1"]],
            marker="o",
            label=f"{label} ({n} músicas pareadas)",
        )
    ax.set(
        xticks=[0, 1],
        xticklabels=["Bateria", "Componente declarado"],
        ylim=(0, 1),
        ylabel="F1 contra o chart",
        title="Comparação somente nos mesmos recortes disponíveis",
    )
    ax.legend()
    ax.grid(alpha=0.2)
    fig.savefig(destination / "03-paired-components.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4), layout="constrained")
    levels = ["low", "medium", "high"]
    for offset, method in [(-0.18, "baseline"), (0.18, "frozen")]:
        cells = [
            next(
                r
                for r in summary["hh_density"]
                if r["mode"] == "mix" and r["method"] == method and r["density_bin"] == level
            )
            for level in levels
        ]
        ax.bar(
            [i + offset for i in range(3)],
            [r["recall"] or 0 for r in cells],
            width=0.36,
            label=method,
        )
    ax.set(
        xticks=range(3),
        xticklabels=["< 2/s", "2 a < 5/s", "≥ 5/s"],
        ylim=(0, 1),
        ylabel="Recall de amarelos do chart",
        xlabel="Densidade de referências no recorte",
        title="Densidade e recuperação — associação descritiva",
    )
    ax.legend()
    ax.grid(axis="y", alpha=0.2)
    fig.savefig(destination / "04-density.png", dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipe", type=Path, required=True)
    parser.add_argument("--reports", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("output exists; choose a new directory")
    recipe = json.loads(args.recipe.read_text())
    state = json.loads((args.reports / "state.json").read_text())
    if json.loads((args.reports / "complete.json").read_text()) != state:
        parser.error("survey is incomplete")
    if state["recipe_sha256"] != shared.digest(args.recipe):
        parser.error("recipe changed")
    rows = observations(recipe, args.reports)
    summary = summarize_survey(rows)
    per_song = []
    for song in recipe["songs"]:
        report = json.loads((args.reports / song["id"] / "report.json").read_text())
        for mode, groups in report["songs"][0]["modes"].items():
            for group, methods in groups.items():
                per_song.append(
                    {
                        "song_id": song["id"],
                        "artist": song["artist"],
                        "title": song["title"],
                        "mode": mode,
                        "group": group,
                        **methods,
                    }
                )
    availability = Counter()
    silent_songs = set()
    duplicate_audio = []
    for song in recipe["songs"]:
        report = json.loads((args.reports / song["id"] / "report.json").read_text())
        for excerpt in report["excerpts"]:
            for item in excerpt["excluded_views"]:
                availability[item["mode"] + ":" + item.get("group", "all")] += 1
                silent_songs.add(song["id"])
        hashes = Counter(
            value
            for name, value in song["assets_sha256"].items()
            if name not in {"song.ini", "notes.mid", "notes.chart"}
        )
        if any(n > 1 for n in hashes.values()):
            duplicate_audio.append(song["id"])
    ranking = []
    for song in recipe["songs"]:
        subset = [
            r
            for r in rows
            if r["song_id"] == song["id"] and r["mode"] == "mix" and r["method"] == "frozen"
        ]
        scores = [summarize([r for r in subset if r["group"] == g]) for g in shared.TARGET_GROUPS]
        valid = [s["f1"] for s in scores if s["tp"] + s["fn"] > 0]
        ranking.append(
            {
                "song_id": song["id"],
                "artist": song["artist"],
                "title": song["title"],
                "mean_class_f1": sum(valid) / len(valid) if valid else None,
            }
        )
    zero_target = [r for r in ranking if r["mean_class_f1"] is None]
    ranking = [r for r in ranking if r["mean_class_f1"] is not None]
    ranking.sort(key=lambda r: r["mean_class_f1"])
    result = {
        "schema_version": 1,
        "method": "frozen_song_survey",
        "analysis_source_sha256": {
            p.name: shared.digest(p)
            for p in [Path(__file__), Path(__file__).with_name("survey_statistics.py")]
        },
        "recipe_sha256": shared.digest(args.recipe),
        "processing_state": state,
        "songs": len(recipe["songs"]),
        "artists": len({identity(s["artist"]) for s in recipe["songs"]}),
        "nominal_mix_seconds": sum(e["duration"] for s in recipe["songs"] for e in s["excerpts"]),
        "calibration_performed": False,
        "offset_fitting_performed": False,
        "model_inference_performed": False,
        "warning": shared.WARNING,
        "summary": summary,
        "source_exclusions": dict(availability),
        "songs_with_silent_exclusions": sorted(silent_songs),
        "songs_with_duplicate_audio_hashes": duplicate_audio,
        "ranking_for_inspection_only": ranking,
        "zero_target_songs": zero_target,
        "per_song": per_song,
        "artist_counts": dict(Counter(identity(s["artist"]) for s in recipe["songs"])),
    }
    args.out.mkdir(parents=True)
    (args.out / "report.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    fields = list(dict.fromkeys(key for row in rows for key in row))
    shared.write_csv(args.out / "excerpt-metrics.csv", rows, fields)
    flat = [
        {k: v for k, v in row.items() if k not in {"baseline", "frozen"}}
        | {
            method + "_" + key: value
            for method in ("baseline", "frozen")
            for key, value in row[method].items()
        }
        for row in per_song
    ]
    shared.write_csv(args.out / "song-metrics.csv", flat, list(flat[0]))
    render(summary, per_song, args.out)

    def number(value):
        return "—" if value is None else f"{value:.3f}"

    table = "".join(
        f"<tr><td>{html.escape(r['artist'])}</td><td>{html.escape(r['title'])}</td>"
        f"<td>{r['mode']}</td><td>{r['group']}</td>"
        f"<td>{r['baseline']['tp'] + r['baseline']['fn']}</td>"
        f"<td>{number(r['baseline']['f1'])}</td>"
        f"<td>{number(r['frozen']['f1'])}</td></tr>"
        for r in per_song
    )
    overview = "".join(
        f"<tr><td>{group}</td><td>{number(cell['baseline']['f1'])}</td>"
        f"<td>{number(cell['frozen']['f1'])}</td>"
        f"<td>{number(cell['frozen']['precision'])}</td>"
        f"<td>{number(cell['frozen']['recall'])}</td>"
        f"<td>{cell['uncertainty']['delta_f1_ci95']}</td></tr>"
        for group, cell in summary["cells"]["mix"].items()
    )
    paired_table = "".join(
        f"<tr><td>{p['left']} → {p['right']}</td><td>{p['group']}</td>"
        f"<td>{p['left_metrics']['songs']}</td><td>{p['left_metrics']['excerpts']}</td>"
        f"<td>{number(p['left_metrics']['f1'])} → {number(p['right_metrics']['f1'])}</td></tr>"
        for p in summary["paired_sources"]
        if p["method"] == "frozen"
    )
    images = "".join(
        '<img style="width:100%" src="data:image/png;base64,'
        + base64.b64encode(p.read_bytes()).decode()
        + '">'
        for p in sorted(args.out.glob("*.png"))
    )
    page = (
        "<!doctype html><meta charset='utf-8'><title>64 músicas — padrões</title>"
        "<style>body{font:15px system-ui;max-width:1150px;margin:30px auto;padding:16px}"
        "td,th{padding:6px;border:1px solid #ccc}table{border-collapse:collapse}</style>"
        f"<h1>{result['songs']} músicas novas, {result['artists']} artistas</h1>"
        "<p>Dois recortes fixos por música, sem recalibrar regras ou ajustar offsets. "
        "Comparação com charts, sem anotações acústicas independentes ou inferência ML.</p>"
        "<h2>Mix — todas as músicas</h2><p>Intervalo do ganho em F1 por 1.000 "
        "reamostragens de músicas inteiras. Precisão/recall são do perfil congelado.</p>"
        "<table><tr><th>Referência</th><th>F1 original</th><th>F1 congelado</th>"
        "<th>Precisão</th><th>Recall</th><th>Intervalo do ganho</th></tr>"
        + overview
        + "</table><h2>Fontes nos mesmos recortes — perfil congelado</h2>"
        "<table><tr><th>Fontes</th><th>Referência</th><th>Músicas</th><th>Recortes</th><th>F1</th></tr>"
        + paired_table
        + "</table>"
        + images
        + "<h2>Métricas por música e fonte</h2>"
        "<p>Use a busca do navegador para localizar músicas.</p>"
        "<table><tr><th>Artista</th><th>Música</th><th>Fonte</th><th>Referência</th><th>Notas</th>"
        "<th>F1 original</th><th>F1 congelado</th></tr>" + table + "</table>"
    )
    (args.out / "report.html").write_text(page, encoding="utf-8")
    print(
        json.dumps(
            {
                "songs": result["songs"],
                "artists": result["artists"],
                "output": str(args.out),
                "mix_f1": {
                    g: {m: v[m]["f1"] for m in ("baseline", "frozen")}
                    for g, v in summary["cells"]["mix"].items()
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
