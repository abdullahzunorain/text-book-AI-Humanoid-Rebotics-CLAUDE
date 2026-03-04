import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  textbookSidebar: [
    {
      type: 'doc',
      id: 'intro/index',
      label: 'Introduction: What is Physical AI',
    },
    {
      type: 'category',
      label: 'Module 1: ROS 2 Fundamentals',
      collapsed: false,
      items: [
        'module1-ros2/architecture',
        'module1-ros2/nodes-topics-services',
        'module1-ros2/python-packages',
        'module1-ros2/launch-files',
        'module1-ros2/urdf',
      ],
    },
    {
      type: 'category',
      label: 'Module 2: Simulation Environments',
      collapsed: false,
      items: [
        'module2-simulation/chapter1-gazebo-basics',
        'module2-simulation/chapter2-gazebo-ros2-integration',
        'module2-simulation/chapter3-unity-robotics',
        'module2-simulation/chapter4-unity-ml-agents',
      ],
    },
    {
      type: 'category',
      label: 'Module 3: NVIDIA Isaac',
      collapsed: false,
      items: [
        'module3-isaac/chapter1-isaac-sim-intro',
        'module3-isaac/chapter2-isaac-gym',
        'module3-isaac/chapter3-isaac-ros2-bridge',
        'module3-isaac/chapter4-isaac-reinforcement-learning',
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action Models',
      collapsed: false,
      items: [
        'module4-vla/chapter1-vla-intro',
        'module4-vla/chapter2-multimodal-models',
        'module4-vla/chapter3-action-chunking',
        'module4-vla/chapter4-vla-robotics',
      ],
    },
  ],
};

export default sidebars;
