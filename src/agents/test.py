


relation = {
    "node_judge_idle": {
      "是": "node_idle",
      "否": "node_extract_category"
    },
    "node_idle": {
      "0": "node_judge_idle"
    },
    "node_extract_category": {
      "0": "node_tool_compare_category"
    },
    "node_tool_compare_category": {
      "0": "node_extract_requirements",
      "1": "uncompare_fur_recom"
    },
    "node_extract_requirements": {
      "0": "node_search_recom"
    },
    "uncompare_fur_recom": {
      "0": "node_judge_idle"
    }
  }




for key,value in relation.items():
    for keyword,next_node in value.items():
        print(key,keyword,next_node)