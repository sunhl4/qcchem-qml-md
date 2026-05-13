import json
import uuid

def generate_id():
    return str(uuid.uuid4())

slides = []
slide_counter = 1

def add_slide(layout="blank", bg="FFFFFF"):
    global slide_counter
    idx = slide_counter
    slide_counter += 1
    slides.append({
        "command": "add",
        "parent": "/",
        "type": "slide",
        "props": {
            "layout": layout,
            "background": bg
        }
    })
    return idx

def add_shape(slide_idx, text, x, y, w, h, font="Georgia", size="18", color="333333", bold="false", align="left", preset="rect", fill="none", line="none", name=None):
    props = {
        "text": text,
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "font": font,
        "size": str(size),
        "color": color,
        "bold": bold,
        "align": align,
        "preset": preset,
        "fill": fill,
        "line": line
    }
    if name:
        props["name"] = name
    slides.append({
        "command": "add",
        "parent": f"/slide[{slide_idx}]",
        "type": "shape",
        "props": props
    })

def add_notes(slide_idx, text):
    slides.append({
        "command": "add",
        "parent": f"/slide[{slide_idx}]",
        "type": "notes",
        "props": {"text": text}
    })

def cover_slide(title, subtitle):
    idx = add_slide(bg="1E2761")
    add_shape(idx, title, "2cm", "7cm", "29.87cm", "3cm", size="44", bold="true", color="FFFFFF", align="center")
    add_shape(idx, subtitle, "2cm", "11cm", "29.87cm", "1.2cm", font="Calibri", size="18", color="CADCFC", align="center")
    add_notes(idx, "开场白，欢迎大家参加组会。")

def section_divider(number, title):
    idx = add_slide(bg="1E2761")
    # Giant number
    add_shape(idx, number, "2cm", "2cm", "29.87cm", "15cm", size="150", bold="true", color="FFFFFF", align="left")
    add_shape(idx, title, "2cm", "8cm", "29.87cm", "3cm", size="44", bold="true", color="FFFFFF", align="center")
    add_notes(idx, f"进入第 {number} 部分：{title}。")

def standard_slide(title, bullets, visual_type="card", visual_data=None):
    idx = add_slide(bg="FFFFFF")
    # Title
    add_shape(idx, title, "1.5cm", "1cm", "30cm", "1.8cm", size="36", bold="true", color="1E2761")
    
    # Left column for text
    y_pos = 3.5
    for b in bullets:
        add_shape(idx, f"• {b}", "1.5cm", f"{y_pos}cm", "14cm", "2.2cm", font="Calibri", size="20", color="333333")
        y_pos += 2.3
        
    # Right column visual
    if visual_type == "card":
        add_shape(idx, "", "16.5cm", "3.5cm", "15cm", "12cm", preset="roundRect", fill="F5F7FA")
        if visual_data:
            add_shape(idx, visual_data.get('title', 'Insight'), "17cm", "4cm", "14cm", "1.5cm", size="24", bold="true", color="1E2761")
            add_shape(idx, visual_data.get('body', ''), "17cm", "6cm", "14cm", "8cm", font="Calibri", size="20", color="333333")
    elif visual_type == "cards_3":
        for i, card in enumerate(visual_data):
            x = 16.5 + i*5.2
            add_shape(idx, "", f"{x}cm", "3.5cm", "4.8cm", "10cm", preset="roundRect", fill="1E2761")
            add_shape(idx, card['title'], f"{x+0.2}cm", "4cm", "4.4cm", "1.5cm", size="20", bold="true", color="FFFFFF", align="center")
            add_shape(idx, card['val'], f"{x+0.2}cm", "6cm", "4.4cm", "3cm", size="36", bold="true", color="CADCFC", align="center")
            add_shape(idx, card['sub'], f"{x+0.2}cm", "10cm", "4.4cm", "3cm", font="Calibri", size="14", color="FFFFFF", align="center")
    
    add_notes(idx, f"讲解内容：{title}。")

def full_card_slide(title, cards):
    idx = add_slide(bg="FFFFFF")
    add_shape(idx, title, "1.5cm", "1cm", "30cm", "1.8cm", size="36", bold="true", color="1E2761")
    
    col_w = (33.87 - 3 - (len(cards)-1)*1) / len(cards)
    for i, c in enumerate(cards):
        x = 1.5 + i*(col_w + 1)
        add_shape(idx, "", f"{x}cm", "4cm", f"{col_w}cm", "12cm", preset="roundRect", fill=c.get('bg', "1E2761"))
        add_shape(idx, c['title'], f"{x+0.2}cm", "4.5cm", f"{col_w-0.4}cm", "2.0cm", size="24", bold="true", color="FFFFFF", align="center")
        add_shape(idx, c['body'], f"{x+0.2}cm", "7cm", f"{col_w-0.4}cm", "8cm", font="Calibri", size="18", color="FFFFFF", align="center")
    add_notes(idx, f"对比卡片讲解：{title}")

def chart_slide(title, chart_title, series1, series2, cats, right_text=""):
    idx = add_slide(bg="FFFFFF")
    add_shape(idx, title, "1.5cm", "1cm", "30cm", "1.8cm", size="36", bold="true", color="1E2761")
    
    slides.append({
        "command": "add",
        "parent": f"/slide[{idx}]",
        "type": "chart",
        "props": {
            "chartType": "column",
            "series1.name": "InQuanto",
            "series1.values": series1,
            "series1.color": "1E2761",
            "series2.name": "Our Platform",
            "series2.values": series2,
            "series2.color": "CADCFC",
            "categories": cats,
            "x": "1.5cm",
            "y": "3.5cm",
            "width": "20cm",
            "height": "14cm",
            "title": chart_title
        }
    })
    
    if right_text:
        add_shape(idx, "", "22.5cm", "3.5cm", "9.8cm", "14cm", preset="roundRect", fill="F5F7FA")
        add_shape(idx, "Insight", "23cm", "4cm", "9cm", "1.2cm", size="20", bold="true", color="1E2761")
        add_shape(idx, right_text, "23cm", "5.5cm", "9cm", "11cm", font="Calibri", size="18", color="333333")
    add_notes(idx, title)


# 1. 封面
cover_slide("量子计算化学与平台架构进展汇报", "构建开源、可审计、产品化的量子计算化学工作流平台")

# Part 1
section_divider("01", "为什么作为硬件公司要做本工程？")
standard_slide("硬件公司的破局点", ["纯做硬件缺乏应用层闭环，难以直接输出价值", "商业对手(如Quantinuum)正在通过全栈产品锁定用户", "我们需要一个对接算力与真实化学场景的桥梁", "让量子优势在材料、药物研发中可见可检证"], "card", {"title":"核心逻辑", "body":"只有掌握从化学输入到量子编译的完整编排层，才能最大化底层硬件的差异化优势，同时引入经典计算和ML/MD生态。"})
full_card_slide("硬件与应用双轮驱动", [
    {"title": "硬件层面", "body": "提供高保真度、大规模式的量子算力，但用户不会直接写量子门", "bg": "1E2761"},
    {"title": "软件编排", "body": "需要通过产品化的Workflow，把化学家的语言自动翻译为硬件任务", "bg": "CADCFC"},
    {"title": "商业壁垒", "body": "拥有自己的QChem平台，可直接面向制药/材料客户提供端到端解决方案", "bg": "2C5F2D"}
])
standard_slide("构建开源工作流平台的战略价值", ["不再受制于第三方商业平台的生态锁定", "能够更灵活地插入我们自研的算法和编译优化(如张量网络)", "与MD(分子动力学)和ML生态深度融合", "通过开源(Apache-2.0)吸引全球学术和产业用户共同完善模型"], "cards_3", [
    {"title": "开源", "val": "生态", "sub": "全球开发者共建"},
    {"title": "审计", "val": "可信", "sub": "Methods直接发论文"},
    {"title": "MD/ML", "val": "融合", "sub": "差异化竞争点"}
])
standard_slide("为什么不能直接用已有的开源工具？", ["现有工具(如Tangelo)多为散装脚本，缺乏产品化体验", "无法实现复杂任务的标准化审计(Repro / Parity)", "在作业队列、容错调度、大体系下折叠等企业级特性上存在短板"], "card", {"title":"结论", "body":"我们需要一个带有工业级纪律的架构，而不仅是一个研究用的工具箱。"})
standard_slide("我们的定位", ["不照搬闭源逻辑，不做散装工具箱", "定位：开源、可审计、可写进论文Methods的计算化学编排平台", "融合InQuanto的工作流纪律与Tangelo的算法广度", "打造我们特有的MD/ML延伸能力"], "card", {"title":"愿景", "body":"成为量子化学研究和工业应用的首选开放平台。"})

# Part 2
section_divider("02", "竞品分析：InQuanto 与 Tangelo")
full_card_slide("InQuanto：商业平台标杆", [
    {"title": "特点", "body": "深度绑定Quantinuum生态(TKET, Nexus, H-Series)", "bg": "1E2761"},
    {"title": "优势", "body": "产品叙事完整，拥有极强的Protocol和Job对象模型", "bg": "2C5F2D"},
    {"title": "劣势", "body": "闭源、厂商锁定严重，外界无法完全检证其底层启发式细节", "bg": "B85042"}
])
standard_slide("InQuanto 工作流原理", ["从化学输入(PySCF)出发，定义Active Space", "Fermion to Qubit映射", "通过Computable和Protocol构建量子作业", "提交到云端(Nexus)执行并回收资源报告"], "card", {"title":"核心思想", "body":"一切皆对象。定义好分子、算法、协议后，形成稳定的计算流。"})
full_card_slide("Tangelo：开源工具箱", [
    {"title": "特点", "body": "SandboxAQ开源的端到端工具包，重研究与教程", "bg": "1E2761"},
    {"title": "优势", "body": "算法极多，支持大量Ansatz、后端(Qiskit/Cirq等)，生态丰富", "bg": "2C5F2D"},
    {"title": "劣势", "body": "统一契约较弱，像散装脚本，缺乏企业级作业管控和严谨输出", "bg": "B85042"}
])
standard_slide("Tangelo 工作流原理", ["定义SecondQuantizedMolecule", "选取Solver(如VQESolver, ADAPTSolver)", "指定Backend执行运算", "获取能量与态信息"], "card", {"title":"流程特点", "body":"流程直白，方便二次开发，但各个模块间的接口没有被严格的对象模型(如Protocol)保护，复现性较弱。"})
chart_slide("工作流与复现性对比(分数)", "平台功能广度得分", "9,8,4,7", "8,9,8,8", "Workflow,Algorithms,MD/ML,Reproducibility", "InQuanto在工作流占优，但MD/ML缺乏；我们将在MD/ML及复现性上超越。")
standard_slide("竞品分析总结", ["InQuanto强在工程与产品体验(对象化，报告化)", "Tangelo强在算法广度和自由度", "二者均在MD/ML延伸上留有空白"], "cards_3", [
    {"title": "InQuanto", "val": "重产品", "sub": "闭源封闭"},
    {"title": "Tangelo", "val": "重算法", "sub": "缺乏纪律"},
    {"title": "Our", "val": "全栈", "sub": "开源+纪律"}
])

# Part 3
section_divider("03", "我们的优劣势与应对策略")
full_card_slide("我们的核心优势", [
    {"title": "架构后发优势", "body": "可以直接汲取两家所长，避免早期的技术债", "bg": "2C5F2D"},
    {"title": "可复现性设计", "body": "设计之初就引入Repro/Parity机制，所有过程全留痕", "bg": "2C5F2D"},
    {"title": "MD与ML融合", "body": "公司自有MD力场和ML积累，直接打通端到端材料设计", "bg": "2C5F2D"}
])
full_card_slide("目前的劣势", [
    {"title": "起步晚", "body": "尚未形成庞大的用户社区和完善的教程生态", "bg": "B85042"},
    {"title": "算法深度", "body": "在高级大体系求解(如复杂碎片法)上仍需逐步追赶", "bg": "B85042"},
    {"title": "商业包装", "body": "尚未形成与云计算平台深度集成的商业化UI前端", "bg": "B85042"}
])
standard_slide("策略：我们要做什么？", ["不做InQuanto的无脑克隆，不强求商业云UI的一比一", "构建开放、可审计(Audit)、可插入的编排层", "把Tangelo的算法装入InQuanto的纪律里", "在ML和自研MD接口上打出差异化长板"], "card", {"title":"总原则", "body":"用纪律管住广度，用开源打败封闭，用生态(MD/ML)拓展边界。"})
standard_slide("竞争定调：P0 到 P3", ["P0: 建立绝对可信的Methods引擎(Repro机制)", "P1: 超越现有开源库的杂乱，实现一等工作流对象", "P2: 深化大体系(Embedding)、QPE与MD/ML的差异化", "P3: 完善产品生态(教程、前端看板、社区)"], "cards_3", [
    {"title": "P0-P1", "val": "可信工作流", "sub": "对标基础能力"},
    {"title": "P2", "val": "MD/ML", "sub": "形成独特壁垒"},
    {"title": "P3", "val": "生态", "sub": "走向商业级产品"}
])

# Part 4
section_divider("04", "接下来的计划与架构设计")
standard_slide("整体架构设计：从前向后填", ["顶层架构预留：经典化学+量子核心+编译/后端+ML/MD", "初期不纠结每个模块的具体算法精度", "先打通骨架，确保YAML配置->执行->Repro报告全链路畅通", "为多后端(Qiskit, IonStack, 云作业)留出API抽象"], "card", {"title":"填坑策略", "body":"先搭好整体的高速公路(架构接口)，然后再往各个模块里填高级车(算法)。"})
full_card_slide("模块间交互流 (Data Flow)", [
    {"title": "输入层", "body": "化学输入(YAML) -> 经典化学(PySCF)得到积分", "bg": "1E2761"},
    {"title": "量子层", "body": "映射/Ansatz -> 构建电路IR并编译", "bg": "CADCFC"},
    {"title": "执行层", "body": "多后端分发 -> 汇总态与能量 -> Repro日志", "bg": "2C5F2D"}
])
standard_slide("第一步：快速复现竞品功能", ["先挑选 InQuanto 和 Tangelo 中最典型的功能(如VQE, DMET)", "使用我们自研的这套框架进行复现", "验证能否用同样的化学输入得到一致的输出(Parity一致性)", "在内部输出对比报告，确认架构灵活性"], "card", {"title":"复现", "body":"这是检验架构承载能力的试金石。"})
standard_slide("第二步：文献复现与新算法支持", ["用我们的框架复现顶级期刊(Nature/Science子刊)中的量子化学实验", "确保生成的Repro JSON可以直接作为论文的Methods附件", "开发支持内部研究员测试新量子算法(如新VQE变种)的插件体系"], "card", {"title":"科研背书", "body":"通过复现文献建立学术界公信力，这比任何广告都有效。"})
standard_slide("第三步：API接入ML与自研MD", ["量子侧输出的能量和力，不再只是终点，而是起点", "对接分子动力学(QMEFDataset, NequIP/MACE hooks)", "训练基于量子高精度的自研分子动力学力场", "利用ML Surrogate替代部分昂贵的量子模拟"], "cards_3", [
    {"title": "QC", "val": "高精度数据", "sub": "能量与力"},
    {"title": "ML", "val": "势函数训练", "sub": "提升规模"},
    {"title": "MD", "val": "大分子演化", "sub": "产业级应用"}
])
standard_slide("最终目标：端到端全连通", ["输入：分子结构与业务需求", "引擎：量子计算+计算化学框架智能拆解计算任务", "放大：通过ML力场扩展到大尺度模拟", "输出：材料性质或药物活性预测"], "card", {"title":"全链路闭环", "body":"不仅解决了如何算得准的问题，更解决了算准了有什么用的问题。"})
standard_slide("近期执行路线 (Roadmap)", ["下个月：冻结Repro schema，打通VQE/ADAPT的基础骨架", "Q3：复现主流架构，推出完善的多后端支持与DMET", "Q4：上线MD/ML接口，跑通内部第一个势函数训练Demo", "长期：迭代算法，打磨开发者文档与VitePress知识库"], "card", {"title":"行动指南", "body":"架构先行，场景驱动，生态制胜。"})
standard_slide("补充架构细节：编译与作业投递", ["后端(BackendSpec)抽象：兼容Statevector与Qiskit", "TKET Bridge：统一接管电路优化和资源度量(Metrics)", "异步作业类比(Nexus Analog)：通过SQLite支持本地高并发", "未来云端入口：预留了HTTP与Job DB的对接点"], "card", {"title":"工程细节", "body":"所有编译和硬件相关的不稳定因素，全部隔离在Backend适配层。"})
standard_slide("补充架构细节：Repro与Parity系统", ["每一条实验配置都生成唯一的Hash", "记录详尽的测算资源：线路数、射击数(shots)、编译开销", "导出标准JSON，作为可回溯、可审计的唯一真理", "这是超越散装脚本库的根本"], "card", {"title":"审计级日志", "body":"可审计性(Auditability)是B端客户采购平台的核心考量。"})
standard_slide("团队协作与质量保证", ["自动化测试(CI)覆盖所有核心路径(Smoke tests)", "在PR阶段执行跨后端一致性校验(Conformance)", "坚持文档即代码，中文工程台账与英文公开文档同步维护"], "card", {"title":"质量控制", "body":"用现代软件工程的方法，做高精尖的量子平台。"})

# 结束页
cover_slide("感谢聆听！", "Q&A 环节")

with open("/Users/shl/nvidia/qcchem-qml-md/deck_build.json", "w", encoding="utf-8") as f:
    json.dump(slides, f, ensure_ascii=False, indent=2)
print(f"Generated {len(slides)} commands.")
