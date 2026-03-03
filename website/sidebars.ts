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
  ],
};

export default sidebars;
