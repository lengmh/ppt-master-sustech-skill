# Chart Expression Vocabulary

The live SUSTech registry has 76 references: 33 upstream numeric charts plus 43 retained visual templates. Select for the actual relationship, retaining the exact `chart/<key>`. These are descriptions, not rankings, quotas, or constraints; zero selections is valid. Construction, binding, styling and export belong to Executor.

## Numeric charts

| Reference | Relationship |
|---|---|
| `chart/line_chart` | Connected values over a continuous axis. |
| `chart/area_chart` | Filled continuous series emphasizing magnitude. |
| `chart/stacked_area_chart` | Layered series showing totals and composition. |
| `chart/dual_axis_line_chart` | Continuous series on separate value scales. |
| `chart/stock_chart` | Open, high, low, close across dates. |
| `chart/waterfall_chart` | Sequential contributions between starting and ending totals. |
| `chart/column_chart` | Category values as vertical lengths. |
| `chart/horizontal_bar_chart` | Category values as horizontal lengths. |
| `chart/grouped_bar_chart` | Series side by side within categories. |
| `chart/stacked_bar_chart` | Category totals split into value-driven segments. |
| `chart/butterfly_chart` | Two datasets mirrored around one category axis. |
| `chart/dumbbell_chart` | Paired values joined to expose gaps. |
| `chart/pareto_chart` | Descending contributions with cumulative share. |
| `chart/bullet_chart` | Actual values, targets, and performance bands. |
| `chart/progress_bar_chart` | Completion as filled portions of bounded tracks. |
| `chart/gauge_chart` | One bounded value on a circular domain. |
| `chart/histogram_chart` | Frequencies across contiguous numeric bins. |
| `chart/box_plot_chart` | Median, quartiles, spread, and outliers. |
| `chart/scatter_chart` | Two numeric variables as x/y position. |
| `chart/bubble_chart` | Two position variables plus magnitude as size. |
| `chart/heatmap_chart` | Row-column values as color intensity. |
| `chart/radar_chart` | Multiple measures on radial axes. |
| `chart/matrix_2x2` | Two numeric dimensions, optionally magnitude as radius. |
| `chart/pie_chart` | Parts of a whole as sector angles. |
| `chart/donut_chart` | Parts of a whole around an open center. |
| `chart/pie_of_pie_chart` | Selected parts expanded into a second pie. |
| `chart/bar_of_pie_chart` | Selected parts expanded into a stacked bar. |
| `chart/treemap_chart` | Parts or hierarchy as nested rectangular areas. |
| `chart/sunburst_chart` | Hierarchy as radial levels and angular spans. |
| `chart/funnel_chart` | Sequential values as stage widths. |
| `chart/sankey_chart` | Magnitude between nodes as connection width. |
| `chart/gantt_chart` | Tasks positioned and sized by time. |
| `chart/word_cloud` | Term weight as type size. |

## Retained SUSTech visual templates

These diagram, table and framework references remain indexed for existing callers; they are not all numeric charts. Exact selection summaries remain in `charts_index.json`.

| Reference |
|---|
| `chart/agenda_list` |
| `chart/arc_anchored_list` |
| `chart/basic_table` |
| `chart/chevron_chain_with_tail` |
| `chart/chevron_process` |
| `chart/circular_stages` |
| `chart/client_server_flow` |
| `chart/comparison_columns` |
| `chart/comparison_table` |
| `chart/concentric_circles` |
| `chart/consulting_table` |
| `chart/feature_matrix_table` |
| `chart/financial_statement_table` |
| `chart/fishbone_diagram` |
| `chart/harvey_balls_table` |
| `chart/hub_inward_arrows` |
| `chart/hub_spoke` |
| `chart/icon_grid` |
| `chart/isometric_stairs` |
| `chart/journey_map` |
| `chart/kpi_cards` |
| `chart/labeled_card` |
| `chart/layered_architecture` |
| `chart/mind_map` |
| `chart/module_composition` |
| `chart/numbered_steps` |
| `chart/pipeline_with_stages` |
| `chart/process_flow` |
| `chart/project_schedule_table` |
| `chart/pros_cons_chart` |
| `chart/pyramid_chart` |
| `chart/pyramid_isometric` |
| `chart/quadrant_bubble_scatter` |
| `chart/quadrant_text_bullets` |
| `chart/roadmap_vertical` |
| `chart/segmented_wheel` |
| `chart/snake_flow` |
| `chart/team_roster` |
| `chart/timeline` |
| `chart/top_down_tree` |
| `chart/venn_diagram` |
| `chart/vertical_list` |
| `chart/vertical_pillars` |
