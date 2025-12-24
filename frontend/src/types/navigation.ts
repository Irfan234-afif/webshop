export interface NavLink {
  label: string
  to: string
  exact?: boolean
}

export interface NavCategory {
  label: string
  items: NavLink[]
}
